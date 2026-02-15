from datetime import datetime, timezone
from sqlalchemy import select, update

from app.core.config import settings
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.models import CertificateSetting, Course, Enrollment, Organization, OrganizationSubscription, User


def run_seed() -> None:
    db = SessionLocal()
    try:
        org = db.scalar(select(Organization).order_by(Organization.id.asc()))
        if not org:
            org = Organization(name="Udaan")
            db.add(org)
            db.commit()
            db.refresh(org)

        sub = db.scalar(select(OrganizationSubscription).where(OrganizationSubscription.organization_id == org.id))
        if not sub:
            sub = OrganizationSubscription(
                organization_id=org.id,
                plan="launch",
                max_admins=1,
                starts_at=datetime.now(timezone.utc),
            )
            db.add(sub)

        super_admin = db.scalar(select(User).where(User.role == "super_admin"))
        if not super_admin:
            super_admin = User(
                role="super_admin",
                full_name=settings.superadmin_full_name,
                email=settings.superadmin_email,
                phone=settings.superadmin_phone,
                grade_or_standard=settings.superadmin_grade,
                password_hash=hash_password(settings.superadmin_password),
            )
            db.add(super_admin)
        else:
            super_admin.full_name = settings.superadmin_full_name
            super_admin.email = settings.superadmin_email
            super_admin.phone = settings.superadmin_phone
            super_admin.grade_or_standard = settings.superadmin_grade
            super_admin.password_hash = hash_password(settings.superadmin_password)

        if settings.admin_email:
            admin = db.scalar(select(User).where(User.role == "admin"))
            if not admin:
                admin = User(
                    role="admin",
                    organization_id=org.id,
                    full_name=settings.admin_full_name,
                    email=settings.admin_email,
                    phone=settings.admin_phone,
                    grade_or_standard=settings.admin_grade,
                    password_hash=hash_password(settings.admin_password),
                )
                db.add(admin)

        # Backfill organization_id for existing data
        db.execute(
            update(User)
            .where(User.organization_id.is_(None), User.role != "super_admin")
            .values(organization_id=org.id)
        )
        db.execute(
            update(Course)
            .where(Course.organization_id.is_(None))
            .values(organization_id=org.id)
        )
        db.execute(
            update(Enrollment)
            .where(Enrollment.organization_id.is_(None))
            .values(organization_id=org.id)
        )

        cert_conf = db.scalar(select(CertificateSetting).limit(1))
        if not cert_conf:
            db.add(CertificateSetting(teacher_name=settings.teacher_name))

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
