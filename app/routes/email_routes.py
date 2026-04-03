import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.auth import get_current_user, require_admin
from app.schemas.email_schemas import EmailInput
from app.services.ai_services import (
    classify_email,
    generate_response,
    explain_classification,
)
from app.database import SessionLocal
from app.models.email_model import EmailLog, UserEmail

import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/emails", tags=["Emails"])


class EditResponse(BaseModel):
    draft_response: str


# 🔥 PROCESS EMAIL
@router.post("/process")
def process_email(email: EmailInput, user=Depends(get_current_user)):
    logger.info("Processing email")

    combined_text = f"{email.subject}\n{email.body}"

    classification = classify_email(combined_text)
    explanation = explain_classification(combined_text, classification)

    draft_response = generate_response(combined_text, user)

    db = SessionLocal()
    try:
        email_record = EmailLog(
            user_id=user.id,
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


# 🔥 GET PENDING EMAILS
@router.get("/pending")
def get_pending_emails(user=Depends(get_current_user)):
    db = SessionLocal()
    try:
        return db.query(EmailLog).filter(
            EmailLog.user_id == user.id,
            EmailLog.status == "PENDING"
        ).all()
    finally:
        db.close()


# 🔥 APPROVE EMAIL (ADMIN ONLY)
@router.post("/approve/{email_id}")
def approve_email(email_id: int, user=Depends(require_admin)):
    db = SessionLocal()
    try:
        email = db.query(EmailLog).filter(
            EmailLog.id == email_id
        ).first()

        if not email:
            raise HTTPException(status_code=404, detail="Email not found")

        email.status = "APPROVED"
        email.approver = user.email
        db.commit()

        return {"message": f"Email {email_id} approved"}

    finally:
        db.close()


# 🔥 GET ALL EMAILS (ADMIN ONLY)
@router.get("/all")
def get_all_emails(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    user=Depends(require_admin)
):
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


# 🔥 REVIEW QUEUE (ADMIN)
@router.get("/review-queue")
def review_queue(user=Depends(require_admin)):
    db = SessionLocal()
    try:
        return db.query(EmailLog).filter(
            EmailLog.status == "PENDING"
        ).order_by(EmailLog.id.desc()).all()
    finally:
        db.close()


# 🔥 EMAIL HISTORY
@router.get("/history")
def email_history(user=Depends(get_current_user)):
    db = SessionLocal()
    try:
        return db.query(EmailLog).filter(
            EmailLog.user_id == user.id,
            EmailLog.status == "SENT"
        ).order_by(EmailLog.id.desc()).all()
    finally:
        db.close()


# 🔥 GET SINGLE EMAIL
@router.get("/{email_id}")
def get_email(email_id: int, user=Depends(get_current_user)):
    db = SessionLocal()
    try:
        email = db.query(EmailLog).filter(
            EmailLog.id == email_id,
            EmailLog.user_id == user.id
        ).first()

        if not email:
            raise HTTPException(status_code=404, detail="Email not found")

        return email

    finally:
        db.close()


# 🔥 GET EXPLANATION
@router.get("/{email_id}/explanation")
def get_explanation(email_id: int, user=Depends(get_current_user)):
    db = SessionLocal()
    try:
        email = db.query(EmailLog).filter(
            EmailLog.id == email_id,
            EmailLog.user_id == user.id
        ).first()

        if not email:
            raise HTTPException(status_code=404, detail="Email not found")

        return json.loads(email.ai_explanation) if email.ai_explanation else {}

    finally:
        db.close()


# 🔥 EDIT RESPONSE
@router.patch("/edit-response/{email_id}")
def edit_response(email_id: int, data: EditResponse, user=Depends(get_current_user)):
    db = SessionLocal()
    try:
        email = db.query(EmailLog).filter(
            EmailLog.id == email_id,
            EmailLog.user_id == user.id
        ).first()

        if not email:
            raise HTTPException(status_code=404, detail="Email not found")

        email.draft_response = data.draft_response
        db.commit()

        return {"message": "Response updated"}

    finally:
        db.close()


# 🔥 REJECT EMAIL
@router.post("/reject/{email_id}")
def reject_email(email_id: int, user=Depends(get_current_user)):
    db = SessionLocal()
    try:
        email = db.query(EmailLog).filter(
            EmailLog.id == email_id,
            EmailLog.user_id == user.id
        ).first()

        if not email:
            raise HTTPException(status_code=404, detail="Email not found")

        email.status = "REJECTED"
        db.commit()

        return {"message": f"Email {email_id} rejected"}

    finally:
        db.close()


# 🔥 SEND EMAIL
@router.post("/send/{email_id}")
def send_email(email_id: int, user=Depends(get_current_user)):
    db = SessionLocal()
    try:
        email = db.query(EmailLog).filter(
            EmailLog.id == email_id,
            EmailLog.user_id == user.id
        ).first()

        if not email:
            raise HTTPException(status_code=404, detail="Email not found")

        if email.status != "APPROVED":
            raise HTTPException(status_code=400, detail="Email must be APPROVED before sending")

        email.status = "SENT"
        db.commit()

        return {"message": f"Email {email_id} sent successfully"}

    finally:
        db.close()


# 🔥 RESEND EMAIL
@router.post("/resend/{email_id}")
def resend_email(email_id: int, user=Depends(get_current_user)):
    db = SessionLocal()
    try:
        email = db.query(EmailLog).filter(
            EmailLog.id == email_id,
            EmailLog.user_id == user.id
        ).first()

        if not email:
            raise HTTPException(status_code=404, detail="Email not found")

        if email.status != "SENT":
            raise HTTPException(status_code=400, detail="Only sent emails can be resent")

        return {"message": f"Email {email_id} resent successfully"}

    finally:
        db.close()


# 🔥 ADD EXTRA EMAIL ACCOUNT
@router.post("/add-email")
def add_email(email: str, password: str, user=Depends(get_current_user)):
    db = SessionLocal()
    try:
        db.add(UserEmail(user_id=user.id, email=email, password=password))
        db.commit()
        return {"message": "Email added"}
    finally:
        db.close()


# 🔥 GET PROFILE
@router.get("/profile")
def get_profile(user=Depends(get_current_user)):
    return user


# 🔥 UPDATE PROFILE
@router.put("/profile")
def update_profile(
    full_name: str,
    signature_name: str,
    company_signature: str,
    user=Depends(get_current_user)
):
    db = SessionLocal()
    try:
        user.full_name = full_name
        user.signature_name = signature_name
        user.company_signature = company_signature

        db.commit()

        return {"message": "Profile updated"}

    finally:
        db.close()