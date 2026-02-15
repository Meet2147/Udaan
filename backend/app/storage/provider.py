from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import settings


class StorageProvider:
    def __init__(self):
        self.root = Path(settings.local_storage_path)
        self.root.mkdir(parents=True, exist_ok=True)

    async def save_upload(self, folder: str, upload: UploadFile) -> str:
        ext = Path(upload.filename or "").suffix or ".bin"
        target_dir = self.root / folder
        target_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{uuid4().hex}{ext}"
        target = target_dir / filename
        content = await upload.read()
        target.write_bytes(content)
        return str(target.relative_to(self.root))

    def resolve(self, key: str) -> Path:
        return self.root / key


storage_provider = StorageProvider()
