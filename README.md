# AI-Ledger

A full-stack FastAPI backend with a hand-built LLM tool-calling agent, RAG-powered semantic
search, and production-grade guardrails (rate limiting, structured logging, metrics, distributed
tracing), backed by a React/TypeScript frontend.

> The full build log, every bug hit and fixed, and the reasoning behind each technical decision
> lives in [`PROJECT_NOTES.md`](./PROJECT_NOTES.md). This README is the overview; that file is
> the detailed engineering journal.

## What's in here

- **A hand-written LLM agent**, not a framework's `AgentExecutor`. The tool-calling loop (describe
  tools as JSON schemas, the model requests one, your code decides whether and how to run it,
  then feeds the result back for a natural-language reply) is built from first principles, so the
  mechanism is actually understood instead of hidden behind a library call.
- **Role-scoped tools.** Which tools even get sent to the model is built dynamically from the
  caller's role. A model can't call a tool it was never told exists.
- **Human-in-the-loop confirmation** for destructive actions. A tool requesting a delete is not
  the same as it happening: the agent proposes, the user confirms, a second explicit call executes
  it.
- **RAG via pgvector and LangChain.** Genuine semantic search over inventory items (a query like
  "something to keep me warm" matches an item named "sweater," with zero keyword overlap),
  filtered per user so search never leaks one person's data to another.
- **Redis-backed token-bucket rate limiting** on the agent endpoint, chosen over a simpler
  fixed-window counter to avoid its known boundary-burst weakness.
- **All three observability pillars**: structured JSON logs (structlog), metrics (Prometheus and
  Grafana), and distributed tracing (OpenTelemetry and Jaeger), each doing the job only it's
  suited for.
- **A real auth system**: JWT plus bcrypt, role-based authorization, ownership checks on every
  mutation, schemas that can't be mass-assigned.
- **A working React frontend**: login and register, full CRUD, and a chat UI that handles both
  plain agent replies and the delete-confirmation flow, styled with Tailwind.

## Tech stack

| Layer | Technology |
|---|---|
| API | FastAPI (Python) |
| Database | PostgreSQL + pgvector, via SQLAlchemy ORM |
| Auth | JWT (PyJWT) + bcrypt (passlib) |
| LLM | Groq (OpenAI-compatible chat completions, tool calling) |
| RAG | LangChain + HuggingFace sentence-transformers (local, CPU-only embeddings) |
| Async tasks | Celery + Redis |
| Rate limiting | Redis, token-bucket algorithm |
| Logging | structlog (structured JSON) |
| Metrics | Prometheus + Grafana |
| Tracing | OpenTelemetry + Jaeger |
| Frontend | React + TypeScript + Vite + Tailwind CSS |
| Testing | Pytest + FastAPI `TestClient` |
| CI/CD | GitHub Actions |
| Containerization | Docker + Docker Compose |

## Architecture

```
                         ┌─────────────┐
                         │   React UI  │
                         │ (Vite + TS) │
                         └──────┬──────┘
                                │ JWT-authenticated REST
                                ▼
┌───────────────────────────────────────────────────────────┐
│                      FastAPI backend                      │
│  auth · items CRUD · /items/chat (agent) · /items/summary │
└───┬──────────┬───────────┬───────────┬───────────┬────────┘
    │          │           │           │           │
    ▼          ▼           ▼           ▼           ▼
┌───────┐  ┌───────┐  ┌─────────┐  ┌────────┐  ┌─────────┐
│Postgres│ │ Redis │  │  Groq   │  │ Celery │  │ Jaeger  │
│+pgvector│ │(rate  │  │ (LLM,   │  │ worker │  │(traces) │
│         │ │limit) │  │tool-use)│  │(async) │  │         │
└───────┘  └───────┘  └─────────┘  └────────┘  └─────────┘
                                                      ▲
                                        ┌─────────────┴──┐
                                        │ Prometheus →    │
                                        │ Grafana (metrics)│
                                        └──────────────────┘
```

Every service above runs as its own container, wired together by `docker-compose.yml`.

## Getting started

### Prerequisites
- Docker + Docker Compose
- Node.js (for the frontend)
- A free [Groq API key](https://console.groq.com)

### 1. Configure environment variables

Create `backend/.env`:
```
SECRET_KEY=<any random string>
GROQ_API_KEY=<your Groq API key>
```

### 2. Start the backend stack

```
docker-compose up -d
```

This brings up the FastAPI backend (`:8000`), Postgres+pgvector, Redis, a Celery worker,
Prometheus (`:9090`), Grafana (`:3000`), and Jaeger (`:16686`).

### 3. Start the frontend

```
cd frontend/frontend-app
npm install
npm run dev
```

Open the printed URL (typically `http://localhost:5173`).

### 4. Try it out

- Register a user, log in.
- Create a few items.
- Ask the chat something like "what items do I have?" or "anything to keep me warm?" (RAG
  search), or "delete my \<item\>" (triggers the confirm-first flow).
- Check `http://localhost:9090` (Prometheus), `http://localhost:3000` (Grafana), and
  `http://localhost:16686` (Jaeger) to see the observability stack in action.

## API overview

| Method | Route | Description |
|---|---|---|
| `POST` | `/users/register` | Create an account |
| `POST` | `/users/login` | Get a JWT (form-encoded, OAuth2 password flow) |
| `GET` / `POST` | `/items/` | List / create items (owner-scoped) |
| `GET` / `PUT` / `DELETE` | `/items/{id}` | Read, update, delete one item (ownership + role checked) |
| `GET` | `/items/summary` | LLM-generated summary of your items |
| `POST` | `/items/chat` | The agent: tool-calling, RAG search, human-in-the-loop delete, rate-limited |
| `GET` | `/metrics` | Prometheus scrape target (admin-only) |

## Project layout

```
backend/
  main.py              # FastAPI routes
  models.py / schemas.py
  auth.py               # JWT + password hashing
  database.py
  llm.py                # Groq client, tool schemas, the agent loop
  rag.py                 # pgvector + LangChain embeddings/search
  rate_limit.py          # Redis token-bucket limiter
  logging_config.py      # structlog setup
  grafana_monitoring.py  # Prometheus metrics + middleware
  tracing.py              # OpenTelemetry/Jaeger setup
  celery_app.py / tasks.py
  tests/
frontend/
  frontend-app/           # React + TypeScript + Vite + Tailwind
docker-compose.yml
prometheus.yml
.github/workflows/ci.yml
PROJECT_NOTES.md          # the full build log: every bug, every decision, why
TALKING_POINTS.md         # interview talking points per concept implemented
```

## Known limitations

A few things are tracked as deliberate, documented gaps rather than silent omissions. Full
detail in [`PROJECT_NOTES.md`](./PROJECT_NOTES.md#known-deliberate-limitations-not-bugs--decisions-made-along-the-way):

- The rate limiter's read-modify-write isn't yet atomic (a Lua-script fix is drafted, not wired in).
- A custom trace span around the LLM call isn't showing up in Jaeger yet (open bug).
- A frontend delete-confirmation edge case where a deleted item can still briefly appear in lists.
- `GET /users/` currently has no auth check.
