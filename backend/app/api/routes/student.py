from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.media.signed_video import generate_video_token
from app.models.models import Certificate, Course, Enrollment, Lecture, LectureProgress, Payment
from app.schemas.student import CompleteResponse, PlayResponse, ProgressUpdate
from app.services.certificate_service import generate_certificate
from app.services.course_service import build_student_course_progress, course_completion_check, mark_complete, mark_progress
from app.services.razorpay_service import create_order
from app.storage.provider import storage_provider
from app.utils.deps import require_student

router = APIRouter(tags=["student"], dependencies=[Depends(require_student)])


def _has_active_enrollment(db: Session, student_id: int, course_id: int) -> bool:
    enrollment = db.scalar(
        select(Enrollment).where(
            and_(Enrollment.student_id == student_id, Enrollment.course_id == course_id, Enrollment.status.in_(["active", "completed"]))
        )
    )
    return bool(enrollment)


@router.get("/courses")
def list_courses(student=Depends(require_student), db: Session = Depends(get_db)):
    stmt = select(Course).order_by(Course.created_at.desc())
    if student.organization_id:
        stmt = stmt.where(Course.organization_id == student.organization_id)
    return db.scalars(stmt).all()


@router.post("/courses/{course_id}/enroll")
def enroll(course_id: int, student=Depends(require_student), db: Session = Depends(get_db)):
    course = db.get(Course, course_id)
    if not course or (student.organization_id and course.organization_id != student.organization_id):
        raise HTTPException(status_code=404, detail="Course not found")

    existing = db.scalar(select(Enrollment).where(and_(Enrollment.student_id == student.id, Enrollment.course_id == course_id)))
    if existing:
        if existing.status == "pending_payment":
            payment = db.scalar(select(Payment).where(Payment.enrollment_id == existing.id))
            if payment and payment.razorpay_order_id:
                return {
                    "id": existing.id,
                    "status": existing.status,
                    "payment": {
                        "provider": "razorpay",
                        "key_id": settings.razorpay_key_id,
                        "amount": payment.amount_inr * 100,
                        "currency": payment.currency,
                        "order_id": payment.razorpay_order_id,
                        "name": course.title,
                        "description": "Course enrollment",
                    },
                }
        return {"id": existing.id, "status": existing.status}

    status = "pending"
    if course.price_inr and course.price_inr > 0:
        status = "pending_payment"

    enrollment = Enrollment(
        student_id=student.id,
        course_id=course_id,
        status=status,
        organization_id=course.organization_id,
    )
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)

    if status == "pending_payment":
        if not settings.razorpay_key_id or not settings.razorpay_key_secret:
            raise HTTPException(status_code=400, detail="Payments not configured")
        commission = int((course.price_inr * settings.superadmin_commission_pct) / 100)
        payment = Payment(
            user_id=student.id,
            organization_id=course.organization_id,
            course_id=course.id,
            enrollment_id=enrollment.id,
            purpose="course_enrollment",
            amount_inr=course.price_inr,
            commission_inr=commission,
            status="created",
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)

        order = create_order(
            amount_inr=course.price_inr,
            receipt=f"enroll_{enrollment.id}",
            notes={"payment_id": str(payment.id), "course_id": str(course.id), "student_id": str(student.id)},
        )
        payment.razorpay_order_id = order.get("id")
        db.commit()

        return {
            "id": enrollment.id,
            "status": enrollment.status,
            "payment": {
                "provider": "razorpay",
                "key_id": settings.razorpay_key_id,
                "amount": order.get("amount"),
                "currency": order.get("currency", "INR"),
                "order_id": order.get("id"),
                "name": course.title,
                "description": "Course enrollment",
            },
        }

    return {"id": enrollment.id, "status": enrollment.status, "message": "Enrollment requested"}


@router.get("/courses/{course_id}")
def course_detail(course_id: int, student=Depends(require_student), db: Session = Depends(get_db)):
    course = db.get(Course, course_id)
    if not course or (student.organization_id and course.organization_id != student.organization_id):
        raise HTTPException(status_code=404, detail="Course not found")
    lectures = db.scalars(select(Lecture).where(Lecture.course_id == course_id).order_by(Lecture.order_index.asc())).all()
    enrollment = db.scalar(select(Enrollment).where(and_(Enrollment.student_id == student.id, Enrollment.course_id == course_id)))
    enrolled = enrollment is not None and enrollment.status in {"active", "completed"}
    return {
        "course": course,
        "enrolled": enrolled,
        "enrollment_status": enrollment.status if enrollment else None,
        "lectures": lectures,
    }


@router.get("/lectures/{lecture_id}/play", response_model=PlayResponse)
def play_lecture(lecture_id: int, student=Depends(require_student), db: Session = Depends(get_db)):
    lecture = db.get(Lecture, lecture_id)
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")

    if not _has_active_enrollment(db, student.id, lecture.course_id):
        raise HTTPException(status_code=403, detail="Not enrolled")

    if not lecture.video_key:
        raise HTTPException(status_code=400, detail="Video not uploaded")

    token = generate_video_token(lecture.id, student.id, expires_in=900)
    signed_url = f"{settings.public_base_url}/media/stream/{lecture.id}?token={token}"
    course = db.get(Course, lecture.course_id)
    watermark = f"{student.email} | {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}"
    return PlayResponse(
        signed_url=signed_url,
        watermark_text=watermark,
        watermark_course=course.title if course else "Course",
        expires_in=900,
    )


@router.post("/lectures/{lecture_id}/progress")
def update_progress(lecture_id: int, payload: ProgressUpdate, student=Depends(require_student), db: Session = Depends(get_db)):
    lecture = db.get(Lecture, lecture_id)
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")
    if not _has_active_enrollment(db, student.id, lecture.course_id):
        raise HTTPException(status_code=403, detail="Not enrolled")

    try:
        progress = mark_progress(db, student.id, lecture_id, payload.watched_seconds)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    if progress.completed and course_completion_check(db, student.id, lecture.course_id):
        generate_certificate(db, student.id, lecture.course_id)

    return {"id": progress.id, "completed": progress.completed, "watched_seconds": progress.watched_seconds}


@router.post("/lectures/{lecture_id}/complete", response_model=CompleteResponse)
def complete_lecture(lecture_id: int, student=Depends(require_student), db: Session = Depends(get_db)):
    lecture = db.get(Lecture, lecture_id)
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")
    if not _has_active_enrollment(db, student.id, lecture.course_id):
        raise HTTPException(status_code=403, detail="Not enrolled")

    progress = mark_complete(db, student.id, lecture_id)
    if progress.completed and course_completion_check(db, student.id, lecture.course_id):
        generate_certificate(db, student.id, lecture.course_id)

    return CompleteResponse(completed=progress.completed)


@router.get("/progress")
def progress(student=Depends(require_student), db: Session = Depends(get_db)):
    return build_student_course_progress(db, student.id)


@router.get("/certificates")
def certificates(student=Depends(require_student), db: Session = Depends(get_db)):
    certs = db.scalars(select(Certificate).where(Certificate.student_id == student.id).order_by(Certificate.issued_at.desc())).all()
    return certs


@router.get("/certificates/{certificate_id}/download")
def download_certificate(certificate_id: int, student=Depends(require_student), db: Session = Depends(get_db)):
    cert = db.get(Certificate, certificate_id)
    if not cert or cert.student_id != student.id:
        raise HTTPException(status_code=404, detail="Certificate not found")
    path = storage_provider.resolve(cert.pdf_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="PDF missing")
    return FileResponse(path, filename=path.name, media_type="application/pdf")
