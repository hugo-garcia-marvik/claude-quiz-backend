# Claude Quiz Backend — Technical Summary

## Tech Stack

### Backend
| Layer | Technology | Version |
|---|---|---|
| Language | Python | 3.11+ |
| Web Framework | FastAPI | 0.115.6 |
| ASGI Server | Uvicorn (with standard extras) | 0.34.0 |
| ORM | SQLAlchemy | 2.0.36 |
| Data Validation | Pydantic v2 | 2.10.4 |
| Settings Management | Pydantic Settings | 2.7.0 |
| Form/Multipart Parsing | Python-Multipart | 0.0.20 |

### Data Layer
| Component | Technology |
|---|---|
| Database Engine | SQLite (file-based: `quiz.db`) |
| ORM | SQLAlchemy 2.x Declarative Base |
| Session Management | `SessionLocal` factory with dependency injection |

### Infrastructure
- No containerization detected (no Dockerfile or docker-compose.yml)
- No CI/CD configuration detected
- Intended for local development execution via `uvicorn`

---

## Architecture Overview

The project is a **monolithic, single-process REST API** following a classic **layered architecture**:

```
HTTP Request
    │
    ▼
┌───────────────────────────────┐
│        FastAPI Router          │  (app/main.py)
│  Route definitions + CORS      │
└────────────┬──────────────────┘
             │
    ┌─────────▼──────────┐
    │  Pydantic Schemas   │  (app/schemas.py)
    │ Request validation  │
    │ Response shaping    │
    └─────────┬──────────┘
              │
   ┌──────────▼─────────┐    ┌─────────────────────┐
   │  Business Logic     │◄───│  Static Quiz Data   │
   │  (in-route handlers)│    │  (app/quiz_data.py) │
   └──────────┬──────────┘    └─────────────────────┘
              │
   ┌──────────▼──────────┐
   │  SQLAlchemy ORM     │  (app/models.py + app/database.py)
   │  Score persistence  │
   └──────────┬──────────┘
              │
   ┌──────────▼──────────┐
   │      SQLite DB       │
   │     (quiz.db)        │
   └──────────────────────┘
```

---

## Key Design Patterns

| Pattern | Where Applied |
|---|---|
| **Dependency Injection** | `get_db()` generator is injected into route handlers via `Depends()` |
| **Schema Separation** | Pydantic schemas are decoupled from ORM models (separate files) |
| **Data Privacy by Design** | Quiz data module exposes a `get_questions_public()` function that strips correct answers before responses are sent to clients |
| **Repository-light Pattern** | Database interactions are performed inline in route handlers using an injected session |
| **Settings Externalization** | `pydantic-settings` is listed as a dependency, indicating support for environment variable–driven configuration |

---

## Directory Structure

```
claude-quiz-backend/
├── README.md               # Project overview and startup instructions (Spanish)
├── requirements.txt        # Python dependency pinning
├── .gitignore              # Ignores .venv, __pycache__, *.db, .env, etc.
└── app/
    ├── __init__.py         # Package marker
    ├── main.py             # FastAPI app instance, CORS config, all route handlers
    ├── database.py         # SQLAlchemy engine, session factory, Base, get_db()
    ├── models.py           # ORM model: Score table
    ├── schemas.py          # Pydantic schemas for requests and responses
    └── quiz_data.py        # Static question bank + helper functions
```

---

## Key Modules / Services

### `app/main.py` — Application Entry Point & Router
- Instantiates the FastAPI app with metadata (title, version, description)
- Configures CORS middleware to allow local frontend dev servers (`localhost:5173`, `localhost:3000`)
- Calls `Base.metadata.create_all(bind=engine)` on startup to auto-create the `scores` table
- Defines all five API endpoints with inline business logic

### `app/quiz_data.py` — Question Bank
- Contains the canonical list of 10 multiple-choice questions as Python dicts
- Each question includes: `id`, `domain`, `question`, `options` (list of 4), `correct_index`, and `explanation`
- `get_questions_public()` — strips `correct_index` and `explanation` before sending to clients
- `get_question_by_id(question_id)` — O(n) lookup by ID used during answer validation

### `app/schemas.py` — Pydantic Data Contracts
| Schema | Purpose |
|---|---|
| `QuestionOut` | Single question sent to client (no answer) |
| `QuizOut` | Full quiz payload (title + questions list) |
| `AnswerItem` | One player answer: `question_id` + `selected_index` (0–3) |
| `SubmitRequest` | Full submission: `player_name` + list of `AnswerItem` |
| `AnswerResult` | Per-question result: `is_correct`, `correct_index`, `explanation` |
| `SubmitResponse` | Full results: score, percentage, per-question results, feedback |
| `LeaderboardEntry` | Ranked player entry with score and rank |
| `LeaderboardOut` | List of leaderboard entries |
| `WelcomeOut` | Welcome message response |

### `app/models.py` — Database ORM Model
- **`Score`** table: `id` (PK), `player_name` (indexed String), `score` (Integer), `total` (Integer, default 10), `created_at` (DateTime UTC)

### `app/database.py` — Data Access Layer
- Creates a SQLite engine pointing to `./quiz.db`
- `SessionLocal`: SQLAlchemy session factory (`autocommit=False`, `autoflush=False`)
- `get_db()`: FastAPI dependency generator that yields and closes a DB session per request

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check — returns `{"status": "ok"}` |
| `GET` | `/api/welcome/{player_name}` | Personalized welcome message |
| `GET` | `/api/quiz` | Returns 10 questions (no correct answers) |
| `POST` | `/api/quiz/submit` | Submits answers; validates, scores, and persists result |
| `GET` | `/api/leaderboard` | Returns top N players (default 10, max 50) |

---

## External Integrations

| Integration | Details |
|---|---|
| **SQLite** | Embedded file-based database; no external DB server required |
| **FastAPI / Swagger UI** | Auto-generated interactive docs at `/docs` and OpenAPI JSON at `/openapi.json` |
| **CORS Origins** | Preconfigured for `http://localhost:3000` and `http://localhost:5173` (typical React/Vite dev servers) |

No third-party APIs, message queues, or external services are used.

---

## Deployment

The project is designed for **local development** only:

```bash
# Setup
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Run
uvicorn app.main:app --reload --port 8000
```

- No Dockerfile, docker-compose, or Kubernetes manifests are present
- No CI/CD pipeline configuration (GitHub Actions, etc.) is present
- The SQLite `quiz.db` file is created automatically on first startup via `create_all()`
- The database file is excluded from version control via `.gitignore`

---

## Testing Approach

- **No test files** are present in the repository
- `.gitignore` excludes `.pytest_cache/` and `.mypy_cache/`, indicating `pytest` and `mypy` are anticipated but not yet configured
- FastAPI's interactive Swagger UI (`/docs`) serves as a manual testing interface

---

## Dependencies

| Package | Version | Purpose |
|---|---|---|
| `fastapi` | 0.115.6 | Web framework: routing, dependency injection, OpenAPI generation |
| `uvicorn[standard]` | 0.34.0 | ASGI server for running FastAPI |
| `sqlalchemy` | 2.0.36 | ORM for database models and query execution |
| `pydantic` | 2.10.4 | Request/response data validation and serialization |
| `pydantic-settings` | 2.7.0 | Environment variable–based configuration management |
| `python-multipart` | 0.0.20 | Form data and file upload parsing (required by FastAPI for form endpoints) |
