# Web-Based Recruitment System

A full-stack web application for managing job postings and applicant tracking. Hiring managers can post jobs and use an AI-powered chat assistant to query applications. Applicants can browse open roles and submit their CV.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python · FastAPI · SQLAlchemy · Alembic |
| Database | PostgreSQL (Docker) · SQLite (local dev) |
| Frontend | React 18 · TypeScript · Vite |
| AI Chat | OpenAI-compatible LLM (LM Studio works out of the box) |
| Container | Docker Compose |

---

## Quick Start (Docker Compose)

### 1. Clone the repository

```bash
git clone https://github.com/abhindix/Web-Based-Recruitment-System.git
cd Web-Based-Recruitment-System
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and set **at minimum**:

| Variable | Description |
|----------|-------------|
| `POSTGRES_PASSWORD` | Strong password for the database |
| `JWT_SECRET` | Random secret for signing JWTs — generate with `python -c "import secrets; print(secrets.token_hex(32))"` |
| `SEED_ADMIN_EMAIL` | (Optional) Email for the first manager account created on startup |
| `SEED_ADMIN_PASSWORD` | (Optional) Password for the first manager account |

### 3. Start the application

```bash
docker compose up --build
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API docs | http://localhost:8000/docs |

---

## Local Development (without Docker)

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Optional: point to a local SQLite DB (default) or set DATABASE_URL
export JWT_SECRET=your_local_secret
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## User Roles

| Role | Description |
|------|-------------|
| `manager` | Can create job postings and use the AI chat assistant |
| `applicant` | Can browse jobs and submit applications with a CV (PDF) |

---

## AI Chat (Optional)

The hiring manager chat uses any OpenAI-compatible endpoint. [LM Studio](https://lmstudio.ai) is supported out of the box:

1. Download and start LM Studio, load a model, and enable its local server.
2. Set in `.env`:
   ```
   LLM_BASE_URL=http://host.docker.internal:1234/v1
   LLM_API_KEY=lm-studio
   LLM_MODEL=<model-id-from-lm-studio-logs>
   ```

To use OpenAI instead:

```
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=sk-...
LLM_MODEL=gpt-4o
```

Leave `LLM_API_KEY` empty to run the app without AI chat.

---

## Email Notifications (Optional)

Application confirmation emails are sent via SMTP. Set the following variables in `.env`:

```
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=user@example.com
SMTP_PASSWORD=your_smtp_password
SMTP_FROM=noreply@example.com
```

When `SMTP_HOST` is empty (the default), the app prints emails to the console instead.

---

## Database Migrations

```bash
cd backend
alembic upgrade head
```

---

## Environment Variables Reference

See [`.env.example`](.env.example) for the full list with descriptions.

---

## License

This project is licensed under the [MIT License](LICENSE).
