from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.session import get_db
from app.models.models import Organization, OrganizationSubscription, User
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


class AdminCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    password: str
    grade_or_standard: str = "NA"


@router.post("/orgs")
def create_org(payload: OrgCreate, db: Session = Depends(get_db)):
    if payload.plan not in PLAN_LIMITS:
        raise HTTPException(status_code=400, detail="Invalid plan")

    existing = db.scalar(select(Organization).where(Organization.name == payload.name))
    if existing:
        raise HTTPException(status_code=400, detail="Organization already exists")

    org = Organization(name=payload.name)
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

    return {"id": org.id, "name": org.name, "plan": sub.plan, "max_admins": sub.max_admins}


@router.get("/orgs")
def list_orgs(db: Session = Depends(get_db)):
    rows = db.scalars(select(Organization).order_by(Organization.created_at.desc())).all()
    return rows


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
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return {"id": admin.id, "email": admin.email, "organization_id": admin.organization_id}
