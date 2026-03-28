# AI Email Assistant

An AI-powered email management system that classifies emails, generates responses, and assists with workflow automation.

---

## Features

* AI-based email classification (category, intent, sentiment, priority)
* Auto-generated professional email replies
* Approval workflow (Approve / Reject emails)
* AI explanation for decisions
* Dashboard UI for email management
* Multi-model support (OpenRouter / LLM APIs)

---

## Tech Stack

**Frontend**

* React (Vite)
* Tailwind CSS

**Backend**

* FastAPI
* Python
* OpenRouter API (LLM)

**Database**

* SQLite (can be upgraded to PostgreSQL)

---

## Setup Instructions

### 1. Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/AI-Email-Classifier.git
cd AI-Email-Classifier
```

---

### 2. Backend Setup

```bash
cd app
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

Create `.env`:

```env
OPENROUTER_API_KEY=your_api_key_here
```

Run backend:

```bash
uvicorn app.main:app --reload --port 8001
```

---

### 3. Frontend Setup

```bash
cd ai-email-frontend
npm install
npm run dev
```

---

## API Endpoints

| Endpoint             | Method | Description              |
| -------------------- | ------ | ------------------------ |
| /emails/process      | POST   | Process & classify email |
| /emails/all          | GET    | Get all emails           |
| /emails/approve/{id} | POST   | Approve email            |
| /emails/reject/{id}  | POST   | Reject email             |

---

## Example Workflow

1. User submits email
2. Backend sends to LLM
3. AI returns classification + response
4. Email stored in DB
5. User approves/rejects via UI

---

## Future Enhancements

* Authentication (JWT)
* Multi-user support
* Email integration (IMAP/Gmail API)
* Admin dashboard
* Analytics & reporting

---

## Author

Ayush Saraswat
