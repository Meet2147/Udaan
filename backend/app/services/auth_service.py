from __future__ import annotations

from datetime import datetime, timezone

from itsdangerous import URLSafeTimedSerializer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    parse_jwt,
    token_hash,
    verify_password,
)
from app.models.models import Organization, RefreshToken, User


from typing import Optional


def _default_org_id(db: Session) -> Optional[int]:
    org = db.scalar(select(Organization).order_by(Organization.id.asc()))
    return org.id if org else None


def signup_student(db: Session, *, full_name: str, email: str, phone: str, grade_or_standard: str, password: str) -> User:
    exists = db.scalar(select(User).where((User.email == email) | (User.phone == phone)))
    if exists:
        raise ValueError("Email or phone already registered")

    org_id = _default_org_id(db)
    user = User(
        role="student",
        organization_id=org_id,
        full_name=full_name,
        email=email,
        phone=phone,
        grade_or_standard=grade_or_standard,
        password_hash=hash_password(password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login(db: Session, email: str, password: str) -> tuple[User, str, str]:
    user = db.scalar(select(User).where(User.email == email))
    if not user or not verify_password(password, user.password_hash):
        raise ValueError("Invalid credentials")

    access_token = create_access_token(str(user.id), user.role)
    refresh_token, expires_at = create_refresh_token(str(user.id), user.role)

    rt = RefreshToken(user_id=user.id, token_hash=token_hash(refresh_token), expires_at=expires_at)
    db.add(rt)
    user.last_active_at = datetime.now(timezone.utc)
    db.commit()

    return user, access_token, refresh_token


def refresh(db: Session, refresh_token: str) -> tuple[str, str]:
    payload = parse_jwt(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise ValueError("Invalid refresh token")

    token_row = db.scalar(select(RefreshToken).where(RefreshToken.token_hash == token_hash(refresh_token)))
    if not token_row or token_row.revoked:
        raise ValueError("Refresh token revoked")

    if token_row.expires_at < datetime.now(timezone.utc):
        raise ValueError("Refresh token expired")

    user = db.get(User, token_row.user_id)
    if not user:
        raise ValueError("User not found")

    token_row.revoked = True
    access = create_access_token(str(user.id), user.role)
    new_refresh, expires_at = create_refresh_token(str(user.id), user.role)
    db.add(RefreshToken(user_id=user.id, token_hash=token_hash(new_refresh), expires_at=expires_at))
    db.commit()
    return access, new_refresh


def logout(db: Session, refresh_token: str) -> None:
    row = db.scalar(select(RefreshToken).where(RefreshToken.token_hash == token_hash(refresh_token)))
    if row:
        row.revoked = True
        db.commit()


def generate_reset_token(email: str) -> str:
    serializer = URLSafeTimedSerializer(settings.secret_key)
    return serializer.dumps({"email": email}, salt="password-reset")


def verify_reset_token(token: str, max_age: int = 3600) -> str:
    serializer = URLSafeTimedSerializer(settings.secret_key)
    data = serializer.loads(token, salt="password-reset", max_age=max_age)
    return data["email"]
