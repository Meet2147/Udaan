from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai import presets
from app.db.session import get_db
from app.models.models import AITransformJob, Organization, User, UserCredit, CreditLedger
from app.schemas.ai import AIHistoryOut
from app.services.ai_service import transform_image
from app.storage.provider import storage_provider
from app.utils.deps import require_student

router = APIRouter(prefix="/ai", tags=["ai"], dependencies=[Depends(require_student)])


class CodingRequest(BaseModel):
    prompt: str


class TopicRequest(BaseModel):
    topic: str


class PlanRequest(BaseModel):
    details: str


@router.post("/transform")
async def transform(
    image: UploadFile = File(...),
    preset: str = Form(...),
    prompt: str | None = Form(default=None),
    student=Depends(require_student),
    db: Session = Depends(get_db),
):
    org = db.get(Organization, student.organization_id) if student.organization_id else None
    if not org or not org.ai_drawing_enabled:
        raise HTTPException(status_code=403, detail="AI drawing not enabled for this organization")

    credit = db.scalar(select(UserCredit).where(UserCredit.user_id == student.id))
    if not credit or credit.balance <= 0:
        raise HTTPException(status_code=402, detail="No drawing credits")

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
    credit.balance -= 1
    db.add(CreditLedger(user_id=student.id, amount=-1, reason="ai_drawing"))
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


@router.get("/config")
def ai_config(student=Depends(require_student), db: Session = Depends(get_db)):
    org = db.get(Organization, student.organization_id) if student.organization_id else None
    credit = db.scalar(select(UserCredit).where(UserCredit.user_id == student.id))
    return {
        "genre": org.genre if org else "general",
        "ai": {
            "drawing": bool(org.ai_drawing_enabled) if org else False,
            "coding": bool(org.ai_coding_enabled) if org else False,
            "general": bool(org.ai_general_enabled) if org else False,
        },
        "credits": credit.balance if credit else 0,
    }


@router.post("/coding")
def coding_pair(payload: CodingRequest, student=Depends(require_student), db: Session = Depends(get_db)):
    org = db.get(Organization, student.organization_id) if student.organization_id else None
    if not org or not org.ai_coding_enabled:
        raise HTTPException(status_code=403, detail="AI coding not enabled for this organization")
    # Placeholder for Sonar API integration
    return {"reply": f"[Sonar placeholder] Pair programming response for: {payload.prompt}"}


@router.post("/general/flashcards")
def gen_flashcards(payload: TopicRequest, student=Depends(require_student), db: Session = Depends(get_db)):
    org = db.get(Organization, student.organization_id) if student.organization_id else None
    if not org or not org.ai_general_enabled:
        raise HTTPException(status_code=403, detail="AI general not enabled for this organization")
    return {"cards": [
        {"q": f"What is {payload.topic}?", "a": "[Sonar placeholder answer]"},
        {"q": f"Key points of {payload.topic}?", "a": "[Sonar placeholder answer]"}
    ]}


@router.post("/general/quiz")
def gen_quiz(payload: TopicRequest, student=Depends(require_student), db: Session = Depends(get_db)):
    org = db.get(Organization, student.organization_id) if student.organization_id else None
    if not org or not org.ai_general_enabled:
        raise HTTPException(status_code=403, detail="AI general not enabled for this organization")
    return {
        "questions": [
            {"q": f"What is {payload.topic}?", "options": ["A", "B", "C", "D"], "answer": "A"}
        ]
    }


@router.post("/general/study-plan")
def gen_plan(payload: PlanRequest, student=Depends(require_student), db: Session = Depends(get_db)):
    org = db.get(Organization, student.organization_id) if student.organization_id else None
    if not org or not org.ai_general_enabled:
        raise HTTPException(status_code=403, detail="AI general not enabled for this organization")
    return {"plan": f"[Sonar placeholder] Study plan for: {payload.details}"}
