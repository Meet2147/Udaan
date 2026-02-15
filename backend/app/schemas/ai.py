from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class AIHistoryOut(BaseModel):
    id: int
    preset: str
    user_prompt: str | None
    input_image_path: str
    output_image_path: str
    created_at: datetime

    class Config:
        from_attributes = True
