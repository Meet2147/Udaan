from __future__ import annotations

import hashlib
import hmac
from typing import Any

import httpx

from app.core.config import settings

BASE_URL = "https://api.razorpay.com/v1"


def _auth() -> tuple[str, str]:
    if not settings.razorpay_key_id or not settings.razorpay_key_secret:
        raise ValueError("Razorpay keys are not configured")
    return settings.razorpay_key_id, settings.razorpay_key_secret


def create_order(*, amount_inr: int, receipt: str, notes: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = {
        "amount": int(amount_inr) * 100,
        "currency": "INR",
        "receipt": receipt,
        "notes": notes or {},
    }
    with httpx.Client(timeout=20) as client:
        res = client.post(f"{BASE_URL}/orders", auth=_auth(), json=payload)
    res.raise_for_status()
    return res.json()


def create_payment_link(
    *,
    amount_inr: int,
    description: str,
    customer: dict[str, Any],
    reference_id: str,
    notes: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = {
        "amount": int(amount_inr) * 100,
        "currency": "INR",
        "description": description,
        "customer": customer,
        "reference_id": reference_id,
        "notify": {"sms": False, "email": True},
        "notes": notes or {},
    }
    with httpx.Client(timeout=20) as client:
        res = client.post(f"{BASE_URL}/payment_links", auth=_auth(), json=payload)
    res.raise_for_status()
    return res.json()


def verify_webhook_signature(body: bytes, signature: str | None) -> bool:
    if not settings.razorpay_webhook_secret:
        return True
    if not signature:
        return False
    expected = hmac.new(
        settings.razorpay_webhook_secret.encode(),
        body,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


def verify_payment_signature(*, order_id: str, payment_id: str, signature: str) -> bool:
    payload = f"{order_id}|{payment_id}".encode()
    expected = hmac.new(settings.razorpay_key_secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
