from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class EnrollmentCreate(BaseModel):
    student_id: int
    course_id: int


class EnrollmentOut(BaseModel):
    id: int
    student_id: int
    course_id: int
    status: str
    enrolled_at: datetime
    completed_at: datetime | None

    class Config:
        from_attributes = True


class ProgressUpdate(BaseModel):
    watched_seconds: int


class CompleteResponse(BaseModel):
    completed: bool


class PlayResponse(BaseModel):
    signed_url: str
    watermark_text: str
    watermark_course: str
    expires_in: int
