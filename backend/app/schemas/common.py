from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class UserOut(BaseModel):
    id: int
    role: str
    full_name: str
    email: str
    phone: str
    grade_or_standard: str
    created_at: datetime

    class Config:
        from_attributes = True
