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

import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/emails", tags=["Emails"])


class EditResponse(BaseModel):
    draft_response: str


# 🔥 PROCESS EMAIL
@router.post("/process")
def process_email(email: EmailInput):
    logger.info("Received email processing request")

    combined_text = f"{email.subject}\n{email.body}"

    logger.info("Running classification")
    classification = classify_email(combined_text)

    logger.info("Generating explanation")
    explanation = explain_classification(combined_text, classification)

    logger.info("Generating draft response")
    draft_response = generate_response(combined_text)

    db = SessionLocal()
    try:
        logger.info("Saving email to database")

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

        logger.info(f"Email stored with ID: {email_record.id}")

        return {
            "email_id": email_record.id,
            "classification": classification,
            "explanation": explanation,
            "draft_response": draft_response,
            "status": email_record.status,
        }

    finally:
        db.close()


# 🔥 GET PENDING
@router.get("/pending")
def get_pending_emails():
    logger.info("Fetching pending emails")

    db = SessionLocal()
    try:
        return db.query(EmailLog).filter(EmailLog.status == "PENDING").all()
    finally:
        db.close()


# 🔥 APPROVE EMAIL
@router.post("/approve/{email_id}")
def approve_email(email_id: int, approver: str = "Manager"):
    logger.info(f"Approve request for email ID: {email_id}")

    db = SessionLocal()
    try:
        email = db.query(EmailLog).filter(EmailLog.id == email_id).first()

        if not email:
            logger.warning(f"Email ID {email_id} not found")
            return {"error": "Email not found"}

        email.status = "APPROVED"
        email.approver = approver
        db.commit()

        logger.info(f"Email {email_id} approved")

        return {"message": f"Email {email_id} approved"}

    finally:
        db.close()


# 🔥 GET ALL (FILTERABLE)
@router.get("/all")
def get_all_emails(status: Optional[str] = None, priority: Optional[str] = None):
    logger.info(f"Fetching emails | status={status}, priority={priority}")

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


# 🔥 REVIEW QUEUE
@router.get("/review-queue")
def review_queue():
    logger.info("Fetching review queue")

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


# 🔥 HISTORY
@router.get("/history")
def email_history():
    logger.info("Fetching email history")

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


# 🔥 GET SINGLE EMAIL
@router.get("/{email_id}")
def get_email(email_id: int):
    logger.info(f"Fetching email ID: {email_id}")

    db = SessionLocal()
    try:
        email = db.query(EmailLog).filter(EmailLog.id == email_id).first()

        if not email:
            logger.warning(f"Email ID {email_id} not found")
            return {"error": "Email not found"}

        return email

    finally:
        db.close()


# 🔥 GET EXPLANATION
@router.get("/{email_id}/explanation")
def get_explanation(email_id: int):
    logger.info(f"Fetching explanation for email ID: {email_id}")

    db = SessionLocal()
    try:
        email = db.query(EmailLog).filter(EmailLog.id == email_id).first()

        if not email:
            logger.warning(f"Email ID {email_id} not found")
            return {"error": "Email not found"}

        return json.loads(email.ai_explanation) if email.ai_explanation else {}

    finally:
        db.close()


# 🔥 EDIT RESPONSE
@router.patch("/edit-response/{email_id}")
def edit_response(email_id: int, data: EditResponse):
    logger.info(f"Editing response for email ID: {email_id}")

    db = SessionLocal()
    try:
        email = db.query(EmailLog).filter(EmailLog.id == email_id).first()

        if not email:
            logger.warning(f"Email ID {email_id} not found")
            return {"error": "Email not found"}

        email.draft_response = data.draft_response
        db.commit()

        logger.info(f"Response updated for email ID: {email_id}")

        return {"message": "Response updated"}

    finally:
        db.close()


# 🔥 REJECT EMAIL
@router.post("/reject/{email_id}")
def reject_email(email_id: int):
    logger.info(f"Rejecting email ID: {email_id}")

    db = SessionLocal()
    try:
        email = db.query(EmailLog).filter(EmailLog.id == email_id).first()

        if not email:
            logger.warning(f"Email ID {email_id} not found")
            return {"error": "Email not found"}

        email.status = "REJECTED"
        db.commit()

        logger.info(f"Email {email_id} rejected")

        return {"message": f"Email {email_id} rejected"}

    finally:
        db.close()


# 🔥 SEND EMAIL
@router.post("/send/{email_id}")
def send_email(email_id: int):
    logger.info(f"Sending email ID: {email_id}")

    db = SessionLocal()
    try:
        email = db.query(EmailLog).filter(EmailLog.id == email_id).first()

        if not email:
            logger.warning(f"Email ID {email_id} not found")
            return {"error": "Email not found"}

        if email.status != "APPROVED":
            logger.warning(f"Email {email_id} not approved yet")
            return {"error": "Email must be APPROVED before sending"}

        logger.info(f"Sending email to {email.sender}")
        logger.info(email.draft_response)

        email.status = "SENT"
        db.commit()

        logger.info(f"Email {email_id} sent successfully")

        return {"message": f"Email {email_id} sent successfully"}

    finally:
        db.close()


# 🔥 RESEND EMAIL
@router.post("/resend/{email_id}")
def resend_email(email_id: int):
    logger.info(f"Resending email ID: {email_id}")

    db = SessionLocal()
    try:
        email = db.query(EmailLog).filter(EmailLog.id == email_id).first()

        if not email:
            logger.warning(f"Email ID {email_id} not found")
            return {"error": "Email not found"}

        if email.status != "SENT":
            logger.warning(f"Email {email_id} is not sent yet")
            return {"error": "Only sent emails can be resent"}

        logger.info(f"Resending email to {email.sender}")
        logger.info(email.draft_response)

        return {"message": f"Email {email_id} resent successfully"}

    finally:
        db.close()