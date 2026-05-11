import email
import base64
import imaplib
import os
from email.header import decode_header
from email.message import Message

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


def _decode_header(value):
    if not value:
        return ""

    parts = []
    for text, charset in decode_header(value):
        if isinstance(text, bytes):
            parts.append(text.decode(charset or "utf-8", errors="replace"))
        else:
            parts.append(text)
    return "".join(parts)


def _plain_text_body(message: Message):
    if message.is_multipart():
        html_fallback = ""
        for part in message.walk():
            content_type = part.get_content_type()
            disposition = str(part.get("Content-Disposition", "")).lower()

            if "attachment" in disposition:
                continue

            payload = part.get_payload(decode=True)
            if not payload:
                continue

            charset = part.get_content_charset() or "utf-8"
            decoded = payload.decode(charset, errors="replace").strip()

            if content_type == "text/plain" and decoded:
                return decoded
            if content_type == "text/html" and decoded and not html_fallback:
                html_fallback = decoded

        return html_fallback

    payload = message.get_payload(decode=True)
    if not payload:
        return str(message.get_payload())

    charset = message.get_content_charset() or "utf-8"
    return payload.decode(charset, errors="replace").strip()


def _normalize_app_password(password):
    return "".join(password.split())


def fetch_emails(email_id, password, limit=5):
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    try:
        mail.login(email_id, _normalize_app_password(password))
        mail.select("inbox")

        _, data = mail.search(None, "ALL")
        mail_ids = data[0].split()

        emails = []

        for num in mail_ids[-limit:]:
            _, msg_data = mail.fetch(num, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])

            emails.append({
                "sender": _decode_header(msg["from"]),
                "subject": _decode_header(msg["subject"]),
                "body": _plain_text_body(msg),
            })

        return emails
    finally:
        try:
            mail.logout()
        except imaplib.IMAP4.error:
            pass


def _gmail_body_from_payload(payload):
    if payload.get("body", {}).get("data"):
        raw_body = payload["body"]["data"]
        return base64.urlsafe_b64decode(raw_body).decode("utf-8", errors="replace")

    for part in payload.get("parts", []):
        mime_type = part.get("mimeType")
        if mime_type == "text/plain":
            body = _gmail_body_from_payload(part)
            if body:
                return body

    for part in payload.get("parts", []):
        body = _gmail_body_from_payload(part)
        if body:
            return body

    return ""


def fetch_google_oauth_emails(account, limit=5):
    scopes = (account.scopes or "https://www.googleapis.com/auth/gmail.readonly").split()
    credentials = Credentials(
        token=account.access_token,
        refresh_token=account.refresh_token,
        token_uri=account.token_uri or "https://oauth2.googleapis.com/token",
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        scopes=scopes,
    )

    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
        account.access_token = credentials.token

    service = build("gmail", "v1", credentials=credentials)
    results = service.users().messages().list(
        userId="me",
        labelIds=["INBOX"],
        maxResults=limit,
    ).execute()

    emails = []
    for message in results.get("messages", []):
        full_message = service.users().messages().get(
            userId="me",
            id=message["id"],
            format="full",
        ).execute()

        headers = {
            header["name"].lower(): header["value"]
            for header in full_message.get("payload", {}).get("headers", [])
        }

        emails.append({
            "sender": headers.get("from", ""),
            "subject": headers.get("subject", ""),
            "body": _gmail_body_from_payload(full_message.get("payload", {})),
        })

    return emails
