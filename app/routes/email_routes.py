import json
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.schemas.email_schemas import EmailInput
from app.services.ai_services import (
    classify_email,
    generate_response,
    explain_classification,
)
from app.database import SessionLocal
from app.models.email_model import EmailLog

router = APIRouter(prefix="/emails", tags=["Emails"])


class EditResponse(BaseModel):
    draft_response: str


@router.post("/process")
def process_email(email: EmailInput):
    combined_text = f"{email.subject}\n{email.body}"

    classification = classify_email(combined_text)
    explanation = explain_classification(combined_text, classification)
    draft_response = generate_response(combined_text)

    db = SessionLocal()
    try:
        email_record = EmailLog(
            sender=email.sender,
            subject=email.subject,
            body=email.body,
            category=classification["category"],
            intent=classification["intent"],
            priority=classification["priority"],
            sentiment=classification["sentiment"],
            draft_response=draft_response,
            status="PENDING",
            approver=None,
            ai_explanation=json.dumps(explanation),
        )

        db.add(email_record)
        db.commit()
        db.refresh(email_record)

        return {
            "email_id": email_record.id,
            "classification": classification,
            "explanation": explanation,
            "draft_response": draft_response,
            "status": email_record.status,
        }
    finally:
        db.close()


@router.get("/pending")
def get_pending_emails():
    db = SessionLocal()
    try:
        return db.query(EmailLog).filter(EmailLog.status == "PENDING").all()
    finally:
        db.close()


@router.post("/approve/{email_id}")
def approve_email(email_id: int, approver: str = "Manager"):
    db = SessionLocal()
    try:
        email = db.query(EmailLog).filter(EmailLog.id == email_id).first()

        if not email:
            return {"error": "Email not found"}

        email.status = "APPROVED"
        email.approver = approver
        db.commit()

        return {"message": f"Email {email_id} approved"}
    finally:
        db.close()


@router.get("/all")
def get_all_emails(status: Optional[str] = None, priority: Optional[str] = None):
    db = SessionLocal()
    try:
        query = db.query(EmailLog)

        if status:
            query = query.filter(EmailLog.status == status)

        if priority:
            query = query.filter(EmailLog.priority == priority)

        return query.order_by(EmailLog.id.desc()).all()
    finally:
        db.close()


@router.get("/review-queue")
def review_queue():
    db = SessionLocal()
    try:
        return (
            db.query(EmailLog)
            .filter(EmailLog.status == "PENDING")
            .order_by(EmailLog.id.desc())
            .all()
        )
    finally:
        db.close()


@router.get("/history")
def email_history():
    db = SessionLocal()
    try:
        return (
            db.query(EmailLog)
            .filter(EmailLog.status == "SENT")
            .order_by(EmailLog.id.desc())
            .all()
        )
    finally:
        db.close()


@router.get("/{email_id}")
def get_email(email_id: int):
    db = SessionLocal()
    try:
        email = db.query(EmailLog).filter(EmailLog.id == email_id).first()

        if not email:
            return {"error": "Email not found"}

        return email
    finally:
        db.close()


@router.get("/{email_id}/explanation")
def get_explanation(email_id: int):
    db = SessionLocal()
    try:
        email = db.query(EmailLog).filter(EmailLog.id == email_id).first()

        if not email:
            return {"error": "Email not found"}

        return json.loads(email.ai_explanation) if email.ai_explanation else {}
    finally:
        db.close()


@router.patch("/edit-response/{email_id}")
def edit_response(email_id: int, data: EditResponse):
    db = SessionLocal()
    try:
        email = db.query(EmailLog).filter(EmailLog.id == email_id).first()

        if not email:
            return {"error": "Email not found"}

        email.draft_response = data.draft_response
        db.commit()

        return {"message": "Response updated"}
    finally:
        db.close()


@router.post("/reject/{email_id}")
def reject_email(email_id: int):
    db = SessionLocal()
    try:
        email = db.query(EmailLog).filter(EmailLog.id == email_id).first()

        if not email:
            return {"error": "Email not found"}

        email.status = "REJECTED"
        db.commit()

        return {"message": f"Email {email_id} rejected"}
    finally:
        db.close()


@router.post("/send/{email_id}")
def send_email(email_id: int):
    db = SessionLocal()
    try:
        email = db.query(EmailLog).filter(EmailLog.id == email_id).first()

        if not email:
            return {"error": "Email not found"}

        if email.status != "APPROVED":
            return {"error": "Email must be APPROVED before sending"}

        print(f"Sending email to {email.sender}...")
        print(email.draft_response)

        email.status = "SENT"
        db.commit()

        return {"message": f"Email {email_id} sent successfully"}
    finally:
        db.close()


@router.post("/resend/{email_id}")
def resend_email(email_id: int):
    db = SessionLocal()
    try:
        email = db.query(EmailLog).filter(EmailLog.id == email_id).first()

        if not email:
            return {"error": "Email not found"}

        if email.status != "SENT":
            return {"error": "Only sent emails can be resent"}

        print(f"Resending email to {email.sender}...")
        print(email.draft_response)

        return {"message": f"Email {email_id} resent successfully"}
    finally:
        db.close()