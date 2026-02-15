from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.models import User
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    ResetPasswordRequest,
    SignupRequest,
    TokenResponse,
)
from app.schemas.common import UserOut
from app.services.auth_service import (
    generate_reset_token,
    login,
    logout,
    refresh,
    signup_student,
    verify_reset_token,
)
from app.core.security import hash_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserOut)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    try:
        user = signup_student(
            db,
            full_name=payload.full_name,
            email=payload.email,
            phone=payload.phone,
            grade_or_standard=payload.grade_or_standard,
            password=payload.password,
        )
        return user
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/login", response_model=TokenResponse)
def login_route(payload: LoginRequest, db: Session = Depends(get_db)):
    try:
        _, access, refresh_token = login(db, payload.email, payload.password)
        return TokenResponse(access_token=access, refresh_token=refresh_token)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/refresh", response_model=TokenResponse)
def refresh_route(payload: RefreshRequest, db: Session = Depends(get_db)):
    try:
        access, new_refresh = refresh(db, payload.refresh_token)
        return TokenResponse(access_token=access, refresh_token=new_refresh)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/logout")
def logout_route(payload: LogoutRequest, db: Session = Depends(get_db)):
    logout(db, payload.refresh_token)
    return {"ok": True}


@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email))
    if not user:
        return {"message": "If email exists, reset link sent"}

    token = generate_reset_token(payload.email)
    return {
        "message": "Email stub generated",
        "reset_token": token,
        "reset_url_example": f"https://example.com/reset?token={token}",
    }


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    try:
        email = verify_reset_token(payload.token)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail="Invalid reset token") from exc

    user = db.scalar(select(User).where(User.email == email))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password_hash = hash_password(payload.new_password)
    user.last_active_at = datetime.now(timezone.utc)
    db.commit()
    return {"ok": True}
