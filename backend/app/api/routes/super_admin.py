from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.session import get_db
from app.core.config import settings
from app.models.models import CreditLedger, Organization, OrganizationSubscription, Payment, User, UserCredit
from app.services.razorpay_service import create_payment_link
from app.utils.deps import require_super_admin

router = APIRouter(prefix="/superadmin", tags=["superadmin"], dependencies=[Depends(require_super_admin)])


PLAN_LIMITS = {
    "launch": 1,
    "rise": 10,
    "scale": 25,
}


class OrgCreate(BaseModel):
    name: str
    plan: str = "launch"
    genre: str = "general"
    ai_drawing_enabled: bool = False
    ai_coding_enabled: bool = False
    ai_general_enabled: bool = True


class AdminCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    password: str
    grade_or_standard: str = "NA"


class OrgUpdate(BaseModel):
    genre: str | None = None
    ai_drawing_enabled: bool | None = None
    ai_coding_enabled: bool | None = None
    ai_general_enabled: bool | None = None


class CreditGrant(BaseModel):
    email: EmailStr
    amount: int
    reason: str = "manual_grant"


@router.post("/orgs")
def create_org(payload: OrgCreate, db: Session = Depends(get_db)):
    if payload.plan not in PLAN_LIMITS:
        raise HTTPException(status_code=400, detail="Invalid plan")

    existing = db.scalar(select(Organization).where(Organization.name == payload.name))
    if existing:
        raise HTTPException(status_code=400, detail="Organization already exists")

    org = Organization(
        name=payload.name,
        genre=payload.genre,
        ai_drawing_enabled=payload.ai_drawing_enabled,
        ai_coding_enabled=payload.ai_coding_enabled,
        ai_general_enabled=payload.ai_general_enabled,
    )
    db.add(org)
    db.commit()
    db.refresh(org)

    sub = OrganizationSubscription(
        organization_id=org.id,
        plan=payload.plan,
        max_admins=PLAN_LIMITS[payload.plan],
        starts_at=datetime.now(timezone.utc),
    )
    db.add(sub)
    db.commit()

    return {
        "id": org.id,
        "name": org.name,
        "plan": sub.plan,
        "max_admins": sub.max_admins,
        "genre": org.genre,
        "ai": {
            "drawing": org.ai_drawing_enabled,
            "coding": org.ai_coding_enabled,
            "general": org.ai_general_enabled,
        },
    }


@router.get("/orgs")
def list_orgs(db: Session = Depends(get_db)):
    rows = db.scalars(select(Organization).order_by(Organization.created_at.desc())).all()
    return rows


@router.put("/orgs/{org_id}")
def update_org(org_id: int, payload: OrgUpdate, db: Session = Depends(get_db)):
    org = db.get(Organization, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    data = payload.model_dump(exclude_none=True)
    for k, v in data.items():
        setattr(org, k, v)
    db.commit()
    db.refresh(org)
    return {
        "id": org.id,
        "name": org.name,
        "genre": org.genre,
        "ai": {
            "drawing": org.ai_drawing_enabled,
            "coding": org.ai_coding_enabled,
            "general": org.ai_general_enabled,
        },
    }


@router.post("/orgs/{org_id}/admins")
def create_org_admin(org_id: int, payload: AdminCreate, db: Session = Depends(get_db)):
    org = db.get(Organization, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    sub = db.scalar(select(OrganizationSubscription).where(OrganizationSubscription.organization_id == org_id))
    if not sub:
        raise HTTPException(status_code=400, detail="Subscription not found")

    admin_count = db.scalar(
        select(func.count(User.id)).where(and_(User.organization_id == org_id, User.role == "admin"))
    ) or 0
    if admin_count >= sub.max_admins:
        raise HTTPException(status_code=400, detail="Admin seat limit reached for this plan")

    existing = db.scalar(select(User).where((User.email == payload.email) | (User.phone == payload.phone)))
    if existing:
        raise HTTPException(status_code=400, detail="Email or phone already registered")

    admin = User(
        role="admin",
        organization_id=org_id,
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
        grade_or_standard=payload.grade_or_standard,
        password_hash=hash_password(payload.password),
        is_active=False,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)

    payment = Payment(
        user_id=admin.id,
        organization_id=org_id,
        purpose="admin_subscription",
        amount_inr=settings.admin_subscription_price_inr,
        commission_inr=0,
        status="created",
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    try:
        link = create_payment_link(
            amount_inr=settings.admin_subscription_price_inr,
            description=f"Udaan Admin Subscription for {org.name}",
            customer={"name": admin.full_name, "email": admin.email, "contact": admin.phone},
            reference_id=str(payment.id),
            notes={"purpose": "admin_subscription", "admin_user_id": str(admin.id), "org_id": str(org_id)},
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    payment.razorpay_payment_link_id = link.get("id")
    payment.razorpay_payment_link_url = link.get("short_url") or link.get("url")
    db.commit()

    return {
        "id": admin.id,
        "email": admin.email,
        "organization_id": admin.organization_id,
        "payment_link_url": payment.razorpay_payment_link_url,
    }


@router.post("/credits")
def grant_credits(payload: CreditGrant, db: Session = Depends(get_db)):
    if payload.amount == 0:
        raise HTTPException(status_code=400, detail="Amount must be non-zero")

    user = db.scalar(select(User).where(User.email == payload.email))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    credit = db.scalar(select(UserCredit).where(UserCredit.user_id == user.id))
    if not credit:
        credit = UserCredit(user_id=user.id, balance=0)
        db.add(credit)

    credit.balance += payload.amount
    db.add(CreditLedger(user_id=user.id, amount=payload.amount, reason=payload.reason))
    db.commit()
    db.refresh(credit)
    return {"user_id": user.id, "email": user.email, "balance": credit.balance}
