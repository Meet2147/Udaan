from __future__ import annotations

from datetime import datetime, timezone

from itsdangerous import BadSignature, URLSafeSerializer

from app.core.config import settings

serializer = URLSafeSerializer(settings.video_signing_secret, salt="video")


def generate_video_token(lecture_id: int, user_id: int, expires_in: int = 900) -> str:
    exp = int(datetime.now(timezone.utc).timestamp()) + expires_in
    return serializer.dumps({"lecture_id": lecture_id, "user_id": user_id, "exp": exp})


def verify_video_token(token: str) -> dict:
    data = serializer.loads(token)
    if data["exp"] < int(datetime.now(timezone.utc).timestamp()):
        raise ValueError("Token expired")
    return data


def safe_verify(token: str) -> dict | None:
    try:
        return verify_video_token(token)
    except (BadSignature, ValueError):
        return None
