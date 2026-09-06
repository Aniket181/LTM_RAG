# Development Log

A chronological record of all development phases, decisions, and changes.

---

## Phase 0 — Project Audit & Planning
**Date:** 2026-09-07
**Status:** ✅ Complete

### Findings
- Python 3.11.9 environment exists (`venvrag/`)
- Git initialized with 1 commit, connected to GitHub (`Aniket181/RAG`)
- Key packages already installed: FastAPI, SQLAlchemy, LangChain, sentence-transformers, ChromaDB, psycopg2, pypdf, torch
- Single placeholder `main.py` file existed

### Decisions Made
- Vector store: ChromaDB for dev → pgvector (PostgreSQL) for prod
- Embedding model: `BAAI/bge-small-en-v1.5` (local, free)
- LLM: Mock mode now → Google Gemini (Phase 10)
- PostgreSQL: Confirmed available
- Frontend: Next.js 14 with App Router

### Architecture Finalized
- 15-phase development roadmap
- Clean modular structure: `backend/app/{api,core,db,models,schemas,eligibility,rag,retrieval,recommendations,ingestion}`

---

## Phase 1 — Project Foundation
**Date:** 2026-09-07
**Status:** ✅ Complete
**Commit:** `feat: initialize project foundation`

### Files Created
| File | Purpose |
|------|---------|
| `.gitignore` | Expanded to cover all project artifacts |
| `.env.example` | All environment variable documentation |
| `README.md` | Project documentation foundation |
| `backend/app/main.py` | FastAPI application factory with lifespan |
| `backend/app/core/config.py` | Pydantic Settings — all config from env |
| `backend/app/core/logging.py` | Structured logging setup |
| `backend/app/core/exceptions.py` | Custom exception hierarchy + handlers |
| `backend/app/api/v1/health.py` | Health check endpoint |
| `backend/app/api/v1/router.py` | API router aggregator |
| `backend/app/api/deps.py` | Shared FastAPI dependencies |
| `backend/tests/conftest.py` | pytest TestClient fixture |
| `backend/tests/integration/test_health_api.py` | 8 health endpoint tests |
| `backend/tests/unit/test_config.py` | 10 config unit tests |
| `backend/pytest.ini` | pytest configuration |
| `docs/development-log.md` | This file |

### Packages Added
| Package | Version | Purpose |
|---------|---------|---------|
| `pytest` | 8.3.5 | Testing framework |
| `pytest-asyncio` | 0.24.0 | Async test support |
| `httpx` | 0.28.1 | HTTP test client |
| `alembic` | 1.14.1 | Database migrations (Phase 2) |

### Test Results
```
18 passed, 1 warning (starlette library warning — not our code)
```

### Key Design Decisions
- Used `asynccontextmanager lifespan` instead of deprecated `@app.on_event`
- `lru_cache` on `get_settings()` ensures Settings are parsed once
- Exception handlers return consistent JSON structure with `success`, `error`, `detail`, `path`
- Health endpoint gracefully handles missing database/vector store (returns `not_configured`)

---

*Next: Phase 2 — Database & Core Models*
