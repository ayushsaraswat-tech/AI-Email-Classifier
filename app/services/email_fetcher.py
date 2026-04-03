import imaplib
import email

def fetch_emails(email_id, password):
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(email_id, password)
    mail.select("inbox")

    _, data = mail.search(None, "ALL")
    mail_ids = data[0].split()

    emails = []

    for num in mail_ids[-5:]:  # last 5 emails
        _, msg_data = mail.fetch(num, "(RFC822)")
        msg = email.message_from_bytes(msg_data[0][1])

        emails.append({
            "sender": msg["from"],
            "subject": msg["subject"],
            "body": str(msg.get_payload())
        })

    return emails