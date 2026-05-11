import json
import logging
import imaplib
import os
from typing import Optional
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, EmailStr
import requests
from googleapiclient.errors import HttpError

from app.auth import create_access_token, get_current_user, verify_token
from app.database import SessionLocal
from app.models.email_model import EmailLog, UserEmail
from app.models.user_model import User
from app.schemas.email_schemas import EmailInput
from app.services.ai_services import (
    classify_email,
    explain_classification,
    generate_response,
)
from app.services.email_fetcher import fetch_emails
from app.services.email_fetcher import fetch_google_oauth_emails

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/emails", tags=["Emails"])

GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid",
]
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"


class EditResponse(BaseModel):
    draft_response: str


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    signature_name: Optional[str] = None
    company_signature: Optional[str] = None


class EmailAccountInput(BaseModel):
    email: EmailStr
    password: str


def _google_oauth_config():
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    redirect_uri = os.getenv(
        "GOOGLE_REDIRECT_URI",
        "http://127.0.0.1:8001/emails/google/callback",
    )

    if not client_id or not client_secret:
        raise HTTPException(
            status_code=500,
            detail=(
                "Google sign-in is not configured yet. Add GOOGLE_CLIENT_ID and "
                "GOOGLE_CLIENT_SECRET to .env from a Google Cloud OAuth client."
            ),
        )

    return {
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
    }


def _imap_auth_error_message(exc):
    raw_message = str(exc)
    if "Application-specific password required" in raw_message:
        return (
            "Gmail requires an app password for IMAP. Turn on 2-Step Verification, "
            "generate a Gmail app password, and save that 16-character password here."
        )

    if "AUTHENTICATIONFAILED" in raw_message:
        return (
            "Gmail rejected the credentials. Use a Gmail app password with IMAP enabled, "
            "not the normal account password."
        )

    return "Gmail could not authenticate this account. Check the app password and IMAP settings."


def _google_api_error_message(exc):
    if getattr(exc, "status_code", None) == 403 or "insufficient" in str(exc).lower():
        return (
            "Google connected this account, but did not grant Gmail read access. "
            "In Google Cloud, add the Gmail readonly scope to the OAuth consent screen, "
            "then remove this account and connect Gmail again."
        )

    return "Google could not fetch Gmail messages for this account. Reconnect Gmail and try again."


def _process_email_record(db, user, incoming):
    combined_text = f"{incoming['subject']}\n{incoming['body']}"

    classification = classify_email(combined_text)
    explanation = explain_classification(combined_text, classification)
    draft_response = generate_response(combined_text, user)

    email_record = EmailLog(
        user_id=user.id,
        sender=incoming["sender"],
        subject=incoming["subject"],
        body=incoming["body"],
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
    return email_record


@router.post("/process")
def process_email(email: EmailInput, user=Depends(get_current_user)):
    logger.info("Processing email")

    db = SessionLocal()
    try:
        email_record = _process_email_record(db, user, {
            "sender": email.sender,
            "subject": email.subject,
            "body": email.body,
        })

        return {
            "email_id": email_record.id,
            "classification": {
                "category": email_record.category,
                "intent": email_record.intent,
                "priority": email_record.priority,
                "sentiment": email_record.sentiment,
            },
            "explanation": json.loads(email_record.ai_explanation) if email_record.ai_explanation else {},
            "draft_response": email_record.draft_response,
            "status": email_record.status,
        }

    finally:
        db.close()


@router.get("/pending")
def get_pending_emails(user=Depends(get_current_user)):
    db = SessionLocal()
    try:
        return db.query(EmailLog).filter(
            EmailLog.user_id == user.id,
            EmailLog.status == "PENDING",
        ).all()
    finally:
        db.close()


@router.post("/approve/{email_id}")
def approve_email(email_id: int, user=Depends(get_current_user)):
    db = SessionLocal()
    try:
        email = db.query(EmailLog).filter(
            EmailLog.id == email_id,
            EmailLog.user_id == user.id,
        ).first()

        if not email:
            raise HTTPException(status_code=404, detail="Email not found")

        email.status = "APPROVED"
        email.approver = user.email
        db.commit()

        return {"message": f"Email {email_id} approved"}

    finally:
        db.close()


@router.get("/all")
def get_all_emails(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    user=Depends(get_current_user),
):
    db = SessionLocal()
    try:
        query = db.query(EmailLog).filter(EmailLog.user_id == user.id)

        if status:
            query = query.filter(EmailLog.status == status)

        if priority:
            query = query.filter(EmailLog.priority == priority)

        return query.order_by(EmailLog.id.desc()).all()
    finally:
        db.close()


@router.get("/review-queue")
def review_queue(user=Depends(get_current_user)):
    db = SessionLocal()
    try:
        return db.query(EmailLog).filter(
            EmailLog.user_id == user.id,
            EmailLog.status == "PENDING",
        ).order_by(EmailLog.id.desc()).all()
    finally:
        db.close()


@router.get("/history")
def email_history(user=Depends(get_current_user)):
    db = SessionLocal()
    try:
        return db.query(EmailLog).filter(
            EmailLog.user_id == user.id,
            EmailLog.status == "SENT",
        ).order_by(EmailLog.id.desc()).all()
    finally:
        db.close()


@router.get("/profile")
def get_profile(user=Depends(get_current_user)):
    db = SessionLocal()
    try:
        connected_emails = db.query(UserEmail).filter(
            UserEmail.user_id == user.id,
        ).order_by(UserEmail.id.asc()).all()

        return {
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "full_name": user.full_name,
            "signature_name": user.signature_name,
            "company_signature": user.company_signature,
            "connected_emails": [
                {
                    "id": account.id,
                    "email": account.email,
                    "is_primary": account.email.lower() == user.email.lower(),
                    "auth_type": account.auth_type or "imap",
                }
                for account in connected_emails
            ],
        }
    finally:
        db.close()


@router.put("/profile")
def update_profile(data: ProfileUpdate, user=Depends(get_current_user)):
    db = SessionLocal()
    try:
        db_user = db.query(User).filter(User.id == user.id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        db_user.full_name = data.full_name
        db_user.signature_name = data.signature_name
        db_user.company_signature = data.company_signature
        db.commit()

        return {"message": "Profile updated"}
    finally:
        db.close()


@router.post("/accounts")
def add_email_account(data: EmailAccountInput, user=Depends(get_current_user)):
    db = SessionLocal()
    try:
        normalized_email = str(data.email).lower()
        existing = db.query(UserEmail).filter(
            UserEmail.user_id == user.id,
            UserEmail.email == normalized_email,
        ).first()

        if existing:
            existing.password = data.password
            existing.auth_type = "imap"
            message = "Email credentials updated"
        else:
            db.add(UserEmail(
                user_id=user.id,
                email=normalized_email,
                password=data.password,
                auth_type="imap",
            ))
            message = "Email added"

        db.commit()
        return {"message": message}
    finally:
        db.close()


@router.get("/accounts")
def list_email_accounts(user=Depends(get_current_user)):
    db = SessionLocal()
    try:
        accounts = db.query(UserEmail).filter(
            UserEmail.user_id == user.id,
        ).order_by(UserEmail.id.asc()).all()

        return [
            {
                "id": account.id,
                "email": account.email,
                "is_primary": account.email.lower() == user.email.lower(),
                "auth_type": account.auth_type or "imap",
            }
            for account in accounts
        ]
    finally:
        db.close()


@router.delete("/accounts/{account_id}")
def delete_email_account(account_id: int, user=Depends(get_current_user)):
    db = SessionLocal()
    try:
        account = db.query(UserEmail).filter(
            UserEmail.id == account_id,
            UserEmail.user_id == user.id,
        ).first()

        if not account:
            raise HTTPException(status_code=404, detail="Email account not found")

        db.delete(account)
        db.commit()

        return {"message": "Email removed"}
    finally:
        db.close()


@router.get("/google/auth-url")
def google_auth_url(user=Depends(get_current_user)):
    state = create_access_token({
        "sub": user.email,
        "purpose": "gmail_oauth",
    })
    google_config = _google_oauth_config()
    authorization_url = f"{GOOGLE_AUTH_URL}?{urlencode({
        'client_id': google_config['client_id'],
        'redirect_uri': google_config['redirect_uri'],
        'response_type': 'code',
        'scope': ' '.join(GMAIL_SCOPES),
        'access_type': 'offline',
        'prompt': 'consent',
        'select_account': 'true',
        'login_hint': user.email,
        'state': state,
    })}"
    return {"authorization_url": authorization_url}


@router.get("/google/callback")
def google_callback(code: str, state: str):
    payload = verify_token(state)
    if not payload or payload.get("purpose") != "gmail_oauth":
        raise HTTPException(status_code=401, detail="Invalid Google connection state")

    google_config = _google_oauth_config()
    token_response = requests.post(
        GOOGLE_TOKEN_URL,
        data={
            "code": code,
            "client_id": google_config["client_id"],
            "client_secret": google_config["client_secret"],
            "redirect_uri": google_config["redirect_uri"],
            "grant_type": "authorization_code",
        },
        timeout=15,
    )
    token_response.raise_for_status()
    token_data = token_response.json()

    userinfo = requests.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": f"Bearer {token_data['access_token']}"},
        timeout=15,
    )
    userinfo.raise_for_status()
    connected_email = userinfo.json().get("email")

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == payload["sub"]).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        normalized_email = connected_email.lower()
        account = db.query(UserEmail).filter(
            UserEmail.user_id == user.id,
            UserEmail.email == normalized_email,
        ).first()

        if not account:
            account = UserEmail(user_id=user.id, email=normalized_email)
            db.add(account)

        account.auth_type = "google_oauth"
        account.password = None
        account.access_token = token_data["access_token"]
        if token_data.get("refresh_token"):
            account.refresh_token = token_data["refresh_token"]
        account.token_uri = GOOGLE_TOKEN_URL
        account.scopes = token_data.get("scope") or " ".join(GMAIL_SCOPES)
        db.commit()

    finally:
        db.close()

    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
    return RedirectResponse(f"{frontend_url}?gmail_connected=1")


@router.post("/fetch-connected")
def fetch_connected_emails(limit: int = 5, user=Depends(get_current_user)):
    db = SessionLocal()
    try:
        accounts = db.query(UserEmail).filter(UserEmail.user_id == user.id).all()
        if not accounts:
            raise HTTPException(
                status_code=400,
                detail="Add the profile email account or an alternate email account before fetching inbox emails",
            )

        imported = []
        errors = []

        for account in accounts:
            try:
                if account.auth_type == "google_oauth":
                    fetched = fetch_google_oauth_emails(account, limit=limit)
                    db.commit()
                else:
                    fetched = fetch_emails(account.email, account.password, limit=limit)
            except imaplib.IMAP4.error as exc:
                logger.warning("Gmail authentication failed for %s: %s", account.email, exc)
                errors.append({
                    "email": account.email,
                    "detail": _imap_auth_error_message(exc),
                })
                continue
            except HttpError as exc:
                logger.warning("Google Gmail API failed for %s: %s", account.email, exc)
                errors.append({
                    "email": account.email,
                    "detail": _google_api_error_message(exc),
                })
                continue
            except Exception as exc:
                logger.exception("Failed to fetch emails for %s", account.email)
                errors.append({"email": account.email, "detail": str(exc)})
                continue

            for incoming in fetched:
                duplicate = db.query(EmailLog).filter(
                    EmailLog.user_id == user.id,
                    EmailLog.sender == incoming["sender"],
                    EmailLog.subject == incoming["subject"],
                    EmailLog.body == incoming["body"],
                ).first()

                if duplicate:
                    continue

                email_record = _process_email_record(db, user, incoming)
                imported.append({
                    "email_id": email_record.id,
                    "source_email": account.email,
                    "subject": email_record.subject,
                })

        if errors and not imported:
            raise HTTPException(status_code=400, detail={
                "message": "No emails were imported because all connected accounts failed.",
                "errors": errors,
            })

        return {
            "imported_count": len(imported),
            "imported": imported,
            "errors": errors,
        }
    finally:
        db.close()


@router.get("/{email_id}")
def get_email(email_id: int, user=Depends(get_current_user)):
    db = SessionLocal()
    try:
        email = db.query(EmailLog).filter(
            EmailLog.id == email_id,
            EmailLog.user_id == user.id,
        ).first()

        if not email:
            raise HTTPException(status_code=404, detail="Email not found")

        return email

    finally:
        db.close()


@router.get("/{email_id}/explanation")
def get_explanation(email_id: int, user=Depends(get_current_user)):
    db = SessionLocal()
    try:
        email = db.query(EmailLog).filter(
            EmailLog.id == email_id,
            EmailLog.user_id == user.id,
        ).first()

        if not email:
            raise HTTPException(status_code=404, detail="Email not found")

        return json.loads(email.ai_explanation) if email.ai_explanation else {}

    finally:
        db.close()


@router.patch("/edit-response/{email_id}")
def edit_response(email_id: int, data: EditResponse, user=Depends(get_current_user)):
    db = SessionLocal()
    try:
        email = db.query(EmailLog).filter(
            EmailLog.id == email_id,
            EmailLog.user_id == user.id,
        ).first()

        if not email:
            raise HTTPException(status_code=404, detail="Email not found")

        email.draft_response = data.draft_response
        db.commit()

        return {"message": "Response updated"}

    finally:
        db.close()


@router.post("/reject/{email_id}")
def reject_email(email_id: int, user=Depends(get_current_user)):
    db = SessionLocal()
    try:
        email = db.query(EmailLog).filter(
            EmailLog.id == email_id,
            EmailLog.user_id == user.id,
        ).first()

        if not email:
            raise HTTPException(status_code=404, detail="Email not found")

        email.status = "REJECTED"
        db.commit()

        return {"message": f"Email {email_id} rejected"}

    finally:
        db.close()


@router.post("/send/{email_id}")
def send_email(email_id: int, user=Depends(get_current_user)):
    db = SessionLocal()
    try:
        email = db.query(EmailLog).filter(
            EmailLog.id == email_id,
            EmailLog.user_id == user.id,
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


@router.post("/resend/{email_id}")
def resend_email(email_id: int, user=Depends(get_current_user)):
    db = SessionLocal()
    try:
        email = db.query(EmailLog).filter(
            EmailLog.id == email_id,
            EmailLog.user_id == user.id,
        ).first()

        if not email:
            raise HTTPException(status_code=404, detail="Email not found")

        if email.status != "SENT":
            raise HTTPException(status_code=400, detail="Only sent emails can be resent")

        return {"message": f"Email {email_id} resent successfully"}

    finally:
        db.close()
