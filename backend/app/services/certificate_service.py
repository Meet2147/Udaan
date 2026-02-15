from __future__ import annotations

from datetime import datetime
from pathlib import Path
from uuid import uuid4

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.models import Certificate, CertificateSetting, Course, User
from app.storage.provider import storage_provider


def get_or_create_settings(db: Session) -> CertificateSetting:
    settings_row = db.scalar(select(CertificateSetting).limit(1))
    if settings_row:
        return settings_row
    settings_row = CertificateSetting(teacher_name=settings.teacher_name)
    db.add(settings_row)
    db.commit()
    db.refresh(settings_row)
    return settings_row


def generate_certificate(db: Session, student_id: int, course_id: int) -> Certificate:
    existing = db.scalar(select(Certificate).where(and_(Certificate.student_id == student_id, Certificate.course_id == course_id)))
    if existing:
        return existing

    student = db.get(User, student_id)
    course = db.get(Course, course_id)
    if not student or not course:
        raise ValueError("Data missing")

    cert_no = f"UDAAN-{datetime.utcnow().strftime('%Y%m%d')}-{uuid4().hex[:8].upper()}"
    folder = Path(settings.local_storage_path) / "certificates"
    folder.mkdir(parents=True, exist_ok=True)
    pdf_name = f"{cert_no}.pdf"
    pdf_path = folder / pdf_name

    conf = get_or_create_settings(db)

    c = canvas.Canvas(str(pdf_path), pagesize=A4)
    width, height = A4
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(width / 2, height - 160, "Certificate of Completion")
    c.setFont("Helvetica", 14)
    c.drawCentredString(width / 2, height - 220, "This certifies that")
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(width / 2, height - 260, student.full_name)
    c.setFont("Helvetica", 14)
    c.drawCentredString(width / 2, height - 300, f"has successfully completed the course '{course.title}'")
    c.drawCentredString(width / 2, height - 330, f"Certificate No: {cert_no}")
    c.drawCentredString(width / 2, height - 360, f"Issued on: {datetime.utcnow().strftime('%Y-%m-%d')}")

    c.setFont("Helvetica", 13)
    c.drawString(80, 120, f"Teacher: {conf.teacher_name}")
    if conf.signature_path:
        sig_file = storage_provider.resolve(conf.signature_path)
        if sig_file.exists():
            c.drawImage(str(sig_file), 80, 140, width=160, height=60, preserveAspectRatio=True, mask="auto")

    c.showPage()
    c.save()

    cert = Certificate(student_id=student_id, course_id=course_id, certificate_no=cert_no, pdf_path=f"certificates/{pdf_name}")
    db.add(cert)
    db.commit()
    db.refresh(cert)
    return cert
