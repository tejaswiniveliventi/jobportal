# Job Portal — Agentic AI Job Application System

## Quick Start

### 1. Copy and fill in environment variables
```bash
cp .env.example .env
# Edit .env — at minimum set GEMINI_API_KEY
# Generate SECRET_KEY: openssl rand -hex 32
```

### 2. Build and start everything
```bash
docker-compose up --build
```

### 3. Open the app
- Frontend: http://localhost:3000
- API docs: http://localhost:8000/docs

---

## Project structure
```
jobportal/
├── docker-compose.yml
├── .env.example
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── alembic/env.py
│   └── app/
│       ├── main.py          # FastAPI app entry point
│       ├── config.py        # All settings via pydantic-settings
│       ├── database.py      # Async SQLAlchemy engine + session
│       ├── celery_app.py    # Celery task queue config
│       ├── models/
│       │   ├── user.py      # User table
│       │   └── application.py  # Job + Application tables
│       ├── schemas/
│       │   ├── auth.py      # Register/login/token schemas
│       │   └── application.py  # App + dashboard schemas
│       ├── core/
│       │   ├── security.py  # JWT + bcrypt
│       │   └── deps.py      # get_current_user dependency
│       ├── routers/
│       │   ├── auth.py      # /auth/register, /login, /refresh, /me
│       │   ├── profile.py   # /profile, /profile/resume, /preferences
│       │   ├── applications.py  # /applications, /dashboard
│       │   └── jobs.py      # /jobs/discover, /approve, /reject
│       ├── agents/
│       │   ├── profile_agent.py    # PDF parse → NER → embed → ChromaDB
│       │   ├── discovery_agent.py  # Adzuna + JSearch API calls
│       │   ├── matcher_agent.py    # Cosine + Gemini scoring
│       │   └── orchestrator.py     # LangGraph state machine
│       └── tasks/
│           ├── profile_tasks.py    # Celery: process resume
│           ├── discovery_tasks.py  # Celery: run discovery cycle
│           └── apply_tasks.py      # Celery: apply (Milestone 4 stub)
└── frontend/
    ├── Dockerfile
    ├── package.json
    ├── vite.config.ts
    ├── tailwind.config.js
    └── src/
        ├── App.tsx
        ├── main.tsx
        ├── index.css
        ├── types/index.ts         # All TypeScript types
        ├── api/
        │   ├── client.ts          # Axios + auto token refresh
        │   ├── auth.ts            # Auth API calls
        │   └── applications.ts    # All other API calls
        ├── store/authStore.ts     # Lightweight user state
        ├── hooks/useApplications.ts  # React Query hooks
        ├── components/
        │   ├── Layout.tsx         # Sidebar + outlet
        │   ├── StatusBadge.tsx    # Coloured status pills
        │   ├── ScoreBar.tsx       # Match score progress bar
        │   ├── ProtectedRoute.tsx # Auth guard
        │   └── Spinner.tsx        # Loading spinner
        └── pages/
            ├── Login.tsx
            ├── Register.tsx
            ├── Dashboard.tsx   # Stats + charts
            ├── Jobs.tsx        # Application list + approve/reject
            ├── Profile.tsx     # Resume upload + preferences
            └── Settings.tsx    # Automation settings
```

## API Keys needed
| Key | Where to get | Free tier |
|-----|-------------|-----------|
| `GEMINI_API_KEY` | aistudio.google.com | 1M tokens/day |
| `ADZUNA_APP_ID` + `ADZUNA_API_KEY` | developer.adzuna.com | 1k req/day |
| `JSEARCH_API_KEY` | rapidapi.com/JSearch | 100 req/day |
| `HUNTER_API_KEY` | hunter.io | 25 req/month |

## What works now (Milestone 1)
- Full Docker stack (Postgres, Redis, FastAPI, Celery, React)
- Auth: register, login, JWT refresh
- Profile: resume upload + async parsing + embedding
- Discovery: Adzuna + JSearch job fetching
- Matching: cosine similarity + Gemini scoring
- Orchestrator: LangGraph coordination
- Dashboard: stats, charts, weekly activity
- Jobs page: approve/reject matched jobs
- Settings: automation preferences

## Next milestone
- Apply Agent: Playwright form automation (Workday, Greenhouse, Lever)
- Connection Agent: Hunter.io hiring manager lookup
- Comms Agent: Cover letter generation
