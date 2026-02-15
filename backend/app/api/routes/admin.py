from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.models import Certificate, CertificateSetting, Course, Enrollment, Lecture, LectureProgress, Organization, User
from app.schemas.course import CourseCreate, CourseOut, CourseUpdate, LectureCreate, LectureOut, LectureUpdate
from app.schemas.student import EnrollmentCreate
from app.services.certificate_service import get_or_create_settings
from app.services.course_service import get_dashboard_stats, list_student_progress
from app.storage.provider import storage_provider
from app.utils.deps import require_admin

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db), user: User = Depends(require_admin)):
    org_id = None if user.role == "super_admin" else user.organization_id
    return get_dashboard_stats(db, organization_id=org_id)


@router.post("/courses", response_model=CourseOut)
def create_course(payload: CourseCreate, db: Session = Depends(get_db), user: User = Depends(require_admin)):
    org_id = user.organization_id
    if user.role == "super_admin" and org_id is None:
        org = db.scalar(select(Organization).order_by(Organization.id.asc()))
        org_id = org.id if org else None
    course = Course(
        level=payload.level.lower(),
        title=payload.title,
        description=payload.description,
        organization_id=org_id,
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@router.get("/courses", response_model=list[CourseOut])
def list_courses(db: Session = Depends(get_db), user: User = Depends(require_admin)):
    stmt = select(Course).order_by(Course.created_at.desc())
    if user.role != "super_admin":
        stmt = stmt.where(Course.organization_id == user.organization_id)
    return db.scalars(stmt).all()


@router.put("/courses/{course_id}", response_model=CourseOut)
def update_course(course_id: int, payload: CourseUpdate, db: Session = Depends(get_db), user: User = Depends(require_admin)):
    course = db.get(Course, course_id)
    if not course or (user.role != "super_admin" and course.organization_id != user.organization_id):
        raise HTTPException(status_code=404, detail="Course not found")
    for key, value in payload.model_dump(exclude_none=True).items():
        setattr(course, key, value)
    db.commit()
    db.refresh(course)
    return course


@router.delete("/courses/{course_id}")
def delete_course(course_id: int, db: Session = Depends(get_db), user: User = Depends(require_admin)):
    course = db.get(Course, course_id)
    if not course or (user.role != "super_admin" and course.organization_id != user.organization_id):
        raise HTTPException(status_code=404, detail="Course not found")
    db.delete(course)
    db.commit()
    return {"ok": True}


@router.post("/courses/{course_id}/lectures", response_model=LectureOut)
def create_lecture(course_id: int, payload: LectureCreate, db: Session = Depends(get_db), user: User = Depends(require_admin)):
    course = db.get(Course, course_id)
    if not course or (user.role != "super_admin" and course.organization_id != user.organization_id):
        raise HTTPException(status_code=404, detail="Course not found")
    lecture = Lecture(
        course_id=course_id,
        title=payload.title,
        description=payload.description,
        duration_sec=payload.duration_sec,
        order_index=payload.order_index,
    )
    db.add(lecture)
    db.commit()
    db.refresh(lecture)
    return lecture


@router.get("/courses/{course_id}/lectures", response_model=list[LectureOut])
def list_lectures(course_id: int, db: Session = Depends(get_db), user: User = Depends(require_admin)):
    course = db.get(Course, course_id)
    if not course or (user.role != "super_admin" and course.organization_id != user.organization_id):
        raise HTTPException(status_code=404, detail="Course not found")
    return db.scalars(select(Lecture).where(Lecture.course_id == course_id).order_by(Lecture.order_index.asc())).all()


@router.put("/courses/{course_id}/lectures/{lecture_id}", response_model=LectureOut)
def update_lecture(course_id: int, lecture_id: int, payload: LectureUpdate, db: Session = Depends(get_db), user: User = Depends(require_admin)):
    lecture = db.get(Lecture, lecture_id)
    if not lecture or lecture.course_id != course_id:
        raise HTTPException(status_code=404, detail="Lecture not found")
    course = db.get(Course, lecture.course_id)
    if course and user.role != "super_admin" and course.organization_id != user.organization_id:
        raise HTTPException(status_code=404, detail="Lecture not found")
    for key, value in payload.model_dump(exclude_none=True).items():
        setattr(lecture, key, value)
    db.commit()
    db.refresh(lecture)
    return lecture


@router.delete("/courses/{course_id}/lectures/{lecture_id}")
def delete_lecture(course_id: int, lecture_id: int, db: Session = Depends(get_db), user: User = Depends(require_admin)):
    lecture = db.get(Lecture, lecture_id)
    if not lecture or lecture.course_id != course_id:
        raise HTTPException(status_code=404, detail="Lecture not found")
    course = db.get(Course, lecture.course_id)
    if course and user.role != "super_admin" and course.organization_id != user.organization_id:
        raise HTTPException(status_code=404, detail="Lecture not found")
    db.delete(lecture)
    db.commit()
    return {"ok": True}


@router.post("/lectures/{lecture_id}/upload")
async def upload_lecture_video(lecture_id: int, video: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(require_admin)):
    lecture = db.get(Lecture, lecture_id)
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")
    course = db.get(Course, lecture.course_id)
    if course and user.role != "super_admin" and course.organization_id != user.organization_id:
        raise HTTPException(status_code=404, detail="Lecture not found")
    key = await storage_provider.save_upload("videos", video)
    lecture.video_key = key
    db.commit()
    return {"video_key": key}


@router.get("/students")
def list_students(db: Session = Depends(get_db), user: User = Depends(require_admin)):
    stmt = select(User).where(User.role == "student").order_by(User.created_at.desc())
    if user.role != "super_admin":
        stmt = stmt.where(User.organization_id == user.organization_id)
    students = db.scalars(stmt).all()
    result = []
    for s in students:
        enrollment_stmt = select(func.count(Enrollment.id)).where(Enrollment.student_id == s.id)
        active_stmt = select(func.count(Enrollment.id)).where(
            and_(Enrollment.student_id == s.id, Enrollment.status.in_(["active", "completed"]))
        )
        if user.role != "super_admin":
            enrollment_stmt = enrollment_stmt.where(Enrollment.organization_id == user.organization_id)
            active_stmt = active_stmt.where(Enrollment.organization_id == user.organization_id)
        enrollment_count = db.scalar(enrollment_stmt) or 0
        active_enrollment = db.scalar(active_stmt) or 0
        result.append(
            {
                "id": s.id,
                "full_name": s.full_name,
                "email": s.email,
                "phone": s.phone,
                "grade_or_standard": s.grade_or_standard,
                "created_at": s.created_at,
                "last_active_at": s.last_active_at,
                "enrollments": enrollment_count,
                "active_enrollments": active_enrollment,
            }
        )
    return result


@router.get("/students/{student_id}/progress")
def student_progress(student_id: int, db: Session = Depends(get_db), user: User = Depends(require_admin)):
    try:
        data = list_student_progress(db, student_id)
        if user.role != "super_admin" and data["student"].get("id"):
            student = db.get(User, student_id)
            if student and student.organization_id != user.organization_id:
                raise HTTPException(status_code=404, detail="Student not found")
        return data
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/enrollments")
def create_or_activate_enrollment(payload: EnrollmentCreate, db: Session = Depends(get_db), user: User = Depends(require_admin)):
    student = db.get(User, payload.student_id)
    course = db.get(Course, payload.course_id)
    if not student or student.role != "student" or not course:
        raise HTTPException(status_code=400, detail="Invalid student/course")
    if user.role != "super_admin" and (student.organization_id != user.organization_id or course.organization_id != user.organization_id):
        raise HTTPException(status_code=400, detail="Invalid student/course")

    existing = db.scalar(
        select(Enrollment).where(and_(Enrollment.student_id == payload.student_id, Enrollment.course_id == payload.course_id))
    )
    if existing:
        existing.status = "active"
        db.commit()
        db.refresh(existing)
        return existing

    enrollment = Enrollment(
        student_id=payload.student_id,
        course_id=payload.course_id,
        status="active",
        organization_id=course.organization_id,
    )
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return enrollment


@router.get("/enrollments")
def list_enrollments(status: str | None = Query(default=None), db: Session = Depends(get_db), user: User = Depends(require_admin)):
    stmt = (
        select(Enrollment, User, Course)
        .join(User, User.id == Enrollment.student_id)
        .join(Course, Course.id == Enrollment.course_id)
        .order_by(Enrollment.enrolled_at.desc())
    )
    if user.role != "super_admin":
        stmt = stmt.where(Enrollment.organization_id == user.organization_id)
    if status:
        stmt = stmt.where(Enrollment.status == status)
    rows = db.execute(stmt).all()
    return [
        {
            "id": enrollment.id,
            "status": enrollment.status,
            "enrolled_at": enrollment.enrolled_at,
            "student_id": user.id,
            "student_name": user.full_name,
            "student_email": user.email,
            "course_id": course.id,
            "course_title": course.title,
            "course_level": course.level,
        }
        for enrollment, user, course in rows
    ]


@router.delete("/enrollments/{enrollment_id}")
def delete_enrollment(enrollment_id: int, db: Session = Depends(get_db), user: User = Depends(require_admin)):
    enrollment = db.get(Enrollment, enrollment_id)
    if not enrollment or (user.role != "super_admin" and enrollment.organization_id != user.organization_id):
        raise HTTPException(status_code=404, detail="Enrollment not found")
    db.delete(enrollment)
    db.commit()
    return {"ok": True}


@router.get("/certificates")
def list_certificates(db: Session = Depends(get_db), user: User = Depends(require_admin)):
    stmt = select(Certificate).order_by(Certificate.issued_at.desc())
    certs = db.scalars(stmt).all()
    out = []
    for c in certs:
        student = db.get(User, c.student_id)
        course = db.get(Course, c.course_id)
        if user.role != "super_admin" and course and course.organization_id != user.organization_id:
            continue
        out.append(
            {
                "id": c.id,
                "certificate_no": c.certificate_no,
                "issued_at": c.issued_at,
                "student_name": student.full_name if student else None,
                "course_title": course.title if course else None,
                "pdf_path": c.pdf_path,
            }
        )
    return out


@router.get("/certificates/{certificate_id}/download")
def download_certificate(certificate_id: int, db: Session = Depends(get_db)):
    cert = db.get(Certificate, certificate_id)
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
    path = storage_provider.resolve(cert.pdf_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="PDF missing")
    return FileResponse(path, filename=path.name, media_type="application/pdf")


@router.post("/settings/certificate-signature")
async def upload_signature(
    teacher_name: str = Form(...), signature: UploadFile | None = File(default=None), db: Session = Depends(get_db)
):
    conf = get_or_create_settings(db)
    conf.teacher_name = teacher_name
    if signature:
        key = await storage_provider.save_upload("signatures", signature)
        conf.signature_path = key
    db.commit()
    return {"teacher_name": conf.teacher_name, "signature_path": conf.signature_path}


@router.get("/settings/certificate")
def certificate_settings(db: Session = Depends(get_db)):
    conf = get_or_create_settings(db)
    return {"teacher_name": conf.teacher_name, "signature_path": conf.signature_path}
