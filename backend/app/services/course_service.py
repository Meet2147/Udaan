from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.models.models import Certificate, Course, Enrollment, Lecture, LectureProgress, User


def get_dashboard_stats(db: Session, organization_id: int | None = None) -> dict:
    student_stmt = select(func.count(User.id)).where(User.role == "student")
    enroll_stmt = select(func.count(func.distinct(Enrollment.student_id))).where(
        Enrollment.status.in_(["active", "completed"])
    )
    if organization_id is not None:
        student_stmt = student_stmt.where(User.organization_id == organization_id)
        enroll_stmt = enroll_stmt.where(Enrollment.organization_id == organization_id)

    total_students = db.scalar(student_stmt) or 0
    enrolled_students = db.scalar(enroll_stmt) or 0
    total_progress = db.scalar(select(func.count(LectureProgress.id))) or 0
    completed_progress = db.scalar(select(func.count(LectureProgress.id)).where(LectureProgress.completed.is_(True))) or 0
    percent = int((completed_progress / total_progress) * 100) if total_progress else 0
    return {
        "total_students": total_students,
        "enrolled_students": enrolled_students,
        "progress_distribution": {"completed_percent": percent, "incomplete_percent": 100 - percent},
    }


def list_student_progress(db: Session, student_id: int) -> dict:
    student = db.get(User, student_id)
    if not student or student.role != "student":
        raise ValueError("Student not found")

    rows = db.execute(
        select(LectureProgress, Lecture, Course)
        .join(Lecture, Lecture.id == LectureProgress.lecture_id)
        .join(Course, Course.id == Lecture.course_id)
        .where(LectureProgress.student_id == student_id)
    ).all()

    progress = [
        {
            "lecture_id": lecture.id,
            "lecture_title": lecture.title,
            "course": course.title,
            "watched_seconds": lp.watched_seconds,
            "completed": lp.completed,
            "updated_at": lp.updated_at,
        }
        for lp, lecture, course in rows
    ]
    return {
        "student": {
            "id": student.id,
            "name": student.full_name,
            "email": student.email,
            "last_active": student.last_active_at,
        },
        "progress": progress,
    }


def course_completion_check(db: Session, student_id: int, course_id: int) -> bool:
    lecture_ids = [x[0] for x in db.execute(select(Lecture.id).where(Lecture.course_id == course_id)).all()]
    if not lecture_ids:
        return False

    completed_count = (
        db.scalar(
            select(func.count(LectureProgress.id)).where(
                and_(
                    LectureProgress.student_id == student_id,
                    LectureProgress.lecture_id.in_(lecture_ids),
                    LectureProgress.completed.is_(True),
                )
            )
        )
        or 0
    )
    done = completed_count == len(lecture_ids)

    if done:
        enrollment = db.scalar(
            select(Enrollment).where(and_(Enrollment.student_id == student_id, Enrollment.course_id == course_id))
        )
        if enrollment and enrollment.status != "completed":
            enrollment.status = "completed"
            enrollment.completed_at = datetime.now(timezone.utc)
            db.commit()
    return done


def mark_progress(db: Session, student_id: int, lecture_id: int, watched_seconds: int) -> LectureProgress:
    lecture = db.get(Lecture, lecture_id)
    if not lecture:
        raise ValueError("Lecture not found")

    progress = db.scalar(
        select(LectureProgress).where(
            and_(LectureProgress.student_id == student_id, LectureProgress.lecture_id == lecture_id)
        )
    )
    if not progress:
        progress = LectureProgress(student_id=student_id, lecture_id=lecture_id, watched_seconds=0, completed=False)
        db.add(progress)

    progress.watched_seconds = max(progress.watched_seconds, watched_seconds)
    if lecture.duration_sec > 0 and progress.watched_seconds >= lecture.duration_sec:
        progress.completed = True
        progress.completed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(progress)
    return progress


def mark_complete(db: Session, student_id: int, lecture_id: int) -> LectureProgress:
    lecture = db.get(Lecture, lecture_id)
    if not lecture:
        raise ValueError("Lecture not found")

    progress = db.scalar(
        select(LectureProgress).where(
            and_(LectureProgress.student_id == student_id, LectureProgress.lecture_id == lecture_id)
        )
    )
    if not progress:
        progress = LectureProgress(student_id=student_id, lecture_id=lecture_id, watched_seconds=lecture.duration_sec)
        db.add(progress)
    progress.completed = True
    progress.completed_at = datetime.now(timezone.utc)
    progress.watched_seconds = max(progress.watched_seconds, lecture.duration_sec)
    db.commit()
    db.refresh(progress)
    return progress


def build_student_course_progress(db: Session, student_id: int) -> list[dict]:
    courses: Iterable[Course] = db.scalars(select(Course)).all()
    output = []
    for course in courses:
        lecture_ids = [x[0] for x in db.execute(select(Lecture.id).where(Lecture.course_id == course.id)).all()]
        total = len(lecture_ids)
        if total:
            completed = (
                db.scalar(
                    select(func.count(LectureProgress.id)).where(
                        and_(
                            LectureProgress.student_id == student_id,
                            LectureProgress.lecture_id.in_(lecture_ids),
                            LectureProgress.completed.is_(True),
                        )
                    )
                )
                or 0
            )
            percent = int((completed / total) * 100)
        else:
            percent = 0
        certificate = db.scalar(
            select(Certificate).where(and_(Certificate.student_id == student_id, Certificate.course_id == course.id))
        )
        output.append(
            {
                "course_id": course.id,
                "course_title": course.title,
                "level": course.level,
                "completed_percent": percent,
                "certificate_available": bool(certificate),
            }
        )
    return output
