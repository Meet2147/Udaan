from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.models import Enrollment, Payment, User
from app.services.razorpay_service import verify_payment_signature, verify_webhook_signature
from app.utils.deps import require_student

router = APIRouter(prefix="/payments", tags=["payments"])


class VerifyPayload(BaseModel):
    order_id: str
    payment_id: str
    signature: str


def _mark_paid(db: Session, payment: Payment, payment_id: str | None = None, signature: str | None = None) -> None:
    if payment.status == "paid":
        return
    if payment_id:
        payment.razorpay_payment_id = payment_id
    if signature:
        payment.razorpay_signature = signature
    payment.status = "paid"

    if payment.purpose == "course_enrollment" and payment.enrollment_id:
        enrollment = db.get(Enrollment, payment.enrollment_id)
        if enrollment:
            enrollment.status = "active"
    if payment.purpose == "admin_subscription" and payment.user_id:
        user = db.get(User, payment.user_id)
        if user:
            user.is_active = True

    db.commit()


@router.post("/verify")
def verify_checkout(payload: VerifyPayload, student=Depends(require_student), db: Session = Depends(get_db)):
    payment = db.scalar(select(Payment).where(Payment.razorpay_order_id == payload.order_id))
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    if not verify_payment_signature(order_id=payload.order_id, payment_id=payload.payment_id, signature=payload.signature):
        raise HTTPException(status_code=400, detail="Invalid payment signature")
    _mark_paid(db, payment, payload.payment_id, payload.signature)
    return {"ok": True}


@router.post("/razorpay/webhook")
async def razorpay_webhook(
    request: Request,
    x_razorpay_signature: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    body = await request.body()
    if not verify_webhook_signature(body, x_razorpay_signature):
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    payload: dict[str, Any] = await request.json()
    event = payload.get("event")

    if event in {"payment.captured", "payment.authorized"}:
        entity = payload.get("payload", {}).get("payment", {}).get("entity", {})
        order_id = entity.get("order_id")
        payment_id = entity.get("id")
        if order_id:
            payment = db.scalar(select(Payment).where(Payment.razorpay_order_id == order_id))
            if payment:
                _mark_paid(db, payment, payment_id, None)
                return {"ok": True}

    if event == "payment_link.paid":
        link = payload.get("payload", {}).get("payment_link", {}).get("entity", {})
        payment_entity = payload.get("payload", {}).get("payment", {}).get("entity", {})
        ref_id = link.get("reference_id")
        payment_id = payment_entity.get("id")
        if ref_id and ref_id.isdigit():
            payment = db.get(Payment, int(ref_id))
            if payment:
                _mark_paid(db, payment, payment_id, None)
                return {"ok": True}

    return {"ok": True}
