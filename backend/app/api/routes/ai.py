from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai import presets
from app.db.session import get_db
from app.models.models import AITransformJob
from app.schemas.ai import AIHistoryOut
from app.services.ai_service import transform_image
from app.storage.provider import storage_provider
from app.utils.deps import require_student

router = APIRouter(prefix="/ai", tags=["ai"], dependencies=[Depends(require_student)])


@router.post("/transform")
async def transform(
    image: UploadFile = File(...),
    preset: str = Form(...),
    prompt: str | None = Form(default=None),
    student=Depends(require_student),
    db: Session = Depends(get_db),
):
    if preset not in presets.PRESETS:
        raise HTTPException(status_code=400, detail="Invalid preset")

    input_key = await storage_provider.save_upload("ai/input", image)
    input_path = storage_provider.resolve(input_key)

    output_dir = Path(storage_provider.root) / "ai" / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_name = f"{input_path.stem}_{preset}.png"
    output_path = output_dir / output_name

    transform_image(str(input_path), str(output_path), preset)
    output_key = str(output_path.relative_to(storage_provider.root))

    job = AITransformJob(
        student_id=student.id,
        input_image_path=input_key,
        preset=preset,
        user_prompt=prompt,
        output_image_path=output_key,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    return {
        "id": job.id,
        "preset": preset,
        "output_image_path": output_key,
        "output_url": f"/media/file/{output_key}",
        "note": "MVP placeholder image transform pipeline; swappable with OpenAI image API adapter.",
    }


@router.get("/history", response_model=list[AIHistoryOut])
def history(student=Depends(require_student), db: Session = Depends(get_db)):
    return db.scalars(select(AITransformJob).where(AITransformJob.student_id == student.id).order_by(AITransformJob.created_at.desc())).all()
