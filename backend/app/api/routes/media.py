from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.media.signed_video import safe_verify
from app.models.models import Enrollment, Lecture
from app.storage.provider import storage_provider

router = APIRouter(prefix="/media", tags=["media"])


@router.get("/stream/{lecture_id}")
def stream_lecture(lecture_id: int, token: str = Query(...), db: Session = Depends(get_db)):
    data = safe_verify(token)
    if not data or int(data["lecture_id"]) != lecture_id:
        raise HTTPException(status_code=403, detail="Invalid token")

    lecture = db.get(Lecture, lecture_id)
    if not lecture or not lecture.video_key:
        raise HTTPException(status_code=404, detail="Video not found")

    enrollment = db.scalar(
        select(Enrollment).where(
            and_(
                Enrollment.student_id == int(data["user_id"]),
                Enrollment.course_id == lecture.course_id,
                Enrollment.status.in_(["active", "completed"]),
            )
        )
    )
    if not enrollment:
        raise HTTPException(status_code=403, detail="Enrollment required")

    path = storage_provider.resolve(lecture.video_key)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Missing file")

    return FileResponse(path, media_type="video/mp4", filename=path.name)


@router.get("/file/{path:path}")
def serve_file(path: str):
    full = storage_provider.resolve(path)
    if not full.exists() or not full.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    if ".." in Path(path).parts:
        raise HTTPException(status_code=400, detail="Invalid path")
    return FileResponse(full)
