# 📡 API Documentation

## Base URL

http://127.0.0.1:8001

---

## 1. Process Email

**POST** `/emails/process`

### Request:

```json
{
  "sender": "user@test.com",
  "subject": "Need help urgently",
  "body": "Please fix my issue"
}
```

### Response:

```json
{
  "category": "Support",
  "intent": "Help Request",
  "priority": "High",
  "sentiment": "Negative",
  "draft_response": "...",
  "ai_explanation": "..."
}
```

---

## 2. Get All Emails

**GET** `/emails/all`

Returns list of processed emails.

---

## 3. Approve Email

**POST** `/emails/approve/{id}`

Marks email as APPROVED.

---

## 4. Reject Email

**POST** `/emails/reject/{id}`

Marks email as REJECTED.
