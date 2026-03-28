# System Architecture

## Overview

The AI Email Assistant is a full-stack application that processes incoming emails using AI models and provides actionable responses.

---

## Components

### 1. Frontend (React)

* Displays email dashboard
* Allows approval/rejection
* Communicates with backend via REST APIs

---

### 2. Backend (FastAPI)

* Handles API requests
* Processes emails using AI service
* Stores results in database

---

### 3. AI Service

* Uses OpenRouter API
* Performs:

  * Classification
  * Response generation
  * Explanation

---

### 4. Database

* Stores email records
* Tracks status (PENDING / APPROVED / REJECTED)

---

## Flow Diagram

1. User submits email
2. Backend receives request
3. AI processes email
4. Data stored in DB
5. Frontend displays results

---

## Future Architecture

* Add authentication layer (JWT)
* Multi-user database
* Email ingestion via IMAP
* Role-based access (Admin/User)
