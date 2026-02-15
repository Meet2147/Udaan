from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class CourseCreate(BaseModel):
    level: str
    title: str
    description: str | None = None


class CourseUpdate(BaseModel):
    level: str | None = None
    title: str | None = None
    description: str | None = None


class CourseOut(BaseModel):
    id: int
    level: str
    title: str
    description: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class LectureCreate(BaseModel):
    title: str
    description: str | None = None
    duration_sec: int = 0
    order_index: int = 1


class LectureUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    duration_sec: int | None = None
    order_index: int | None = None


class LectureOut(BaseModel):
    id: int
    course_id: int
    title: str
    description: str | None
    video_key: str | None
    duration_sec: int
    order_index: int

    class Config:
        from_attributes = True
