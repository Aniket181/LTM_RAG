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

## Phase 12 — Frontend Dashboard (Accelerated)
**Date:** 2026-09-07
**Status:** ✅ Complete
**Commit:** `22a3e99` — `feat: add student opportunity dashboard (frontend)`

> Note: Built ahead of schedule (before Phases 2–11) to establish the full UI layer.
> All backend-dependent features use mock data structured identically to real API schemas.
> Connecting real APIs requires only swapping mock data imports for API client calls.

### Tech Stack
- Next.js 16.3.4 (App Router) + TypeScript
- Tailwind CSS + custom CSS design system
- lucide-react (icons), framer-motion, axios

### Pages Built (7 total)

| Route | Page | Status |
|-------|------|--------|
| `/` | Dashboard | ✅ Live health API + mock recommendations |
| `/profile` | Student Profile | ✅ Full form with completeness meter |
| `/opportunities` | Search | ✅ Real-time filter by type/level/status/text |
| `/opportunities/[id]` | Detail | ✅ Eligibility rules + score breakdown + docs |
| `/recommendations` | Recommendations | ✅ Expandable cards with rule breakdown |
| `/chat` | AI Assistant | ✅ Mock RAG with source citations |
| `/sources` | Source Documents | ✅ Document status + chunk counts |

### Key Architecture Files
| File | Purpose |
|------|---------|
| `src/lib/types.ts` | TypeScript types matching backend Pydantic schemas exactly |
| `src/lib/api.ts` | Typed axios client for all API endpoints |
| `src/lib/mock-data.ts` | 8 real scholarship records + 5 source documents |
| `src/app/globals.css` | Premium dark design system (glassmorphism, gradients, animations) |
| `src/components/layout/Sidebar.tsx` | Persistent navigation with active route detection |

### Design System
- Dark glassmorphism theme (deep navy + electric indigo)
- CSS custom properties for consistent theming
- Reusable component classes: `.card`, `.badge-*`, `.btn-*`, `.glass`, `.rule-row`
- Animations: fadeInUp, float, pulse-glow, shimmer skeleton loader, typing indicator

### Build Verification
```
✓ Compiled successfully (6.7s)
✓ TypeScript: 0 errors
✓ 9/9 pages generated (8 routes + not-found)
✓ HTTP 200 from localhost:3000 (36KB response)
```

### Mock Data Strategy
All scholarship data is sourced from real official schemes (CSSS, AICTE Pragati, AICTE Saksham,
PMSS, UGC Indira Gandhi, Post-Matric SC, INSPIRE, NSP Pre-Matric Minority).
Every record includes `last_verified_date`, `source_url`, and `academic_year`.
The UI shows a disclaimer on every page advising users to verify from official sources.

---

## Phase 2 — Database & Core Models
**Date:** 2026-09-11
**Status:** ✅ Complete
**Commit:** `feat: add database and core models (postgresql docker)`

### Architecture & Deliverables
- **Docker Compose**: Containerized PostgreSQL 16 using `pgvector/pgvector:pg16` with persistent volumes and health check.
- **Environment**: `.env` configured with default local database settings.
- **SQLAlchemy 2.0 Base & Session**:
  - `app.db.base`: `Base`, `UUIDPrimaryKeyMixin`, `TimestampMixin` with UTC support.
  - `app.db.session`: Engine configuration with connection pooling (`pool_pre_ping=True`) and `get_db` FastAPI dependency.
  - `app.db.init_db`: Table initialization and connectivity check utilities.
- **ORM Models**:
  - `Student` (`app.models.student`): Complete demographic, academic, domicile, and interest attributes.
  - `Opportunity` (`app.models.opportunity`): Comprehensive opportunity schema with income, CGPA, category, and eligibility criteria.
  - `SourceDocument` & `DocumentChunk` (`app.models.document`): Ingestion status, source metadata, and chunk passages.
  - `EligibilityCheckLog` (`app.models.eligibility_check_log`): Auditable evaluation trail with JSON rule results.
- **Pydantic Validation Schemas**:
  - `app.schemas.student`: `StudentCreate`, `StudentUpdate`, `StudentResponse`.
  - `app.schemas.opportunity`: `OpportunityCreate`, `OpportunityUpdate`, `OpportunityResponse`, `OpportunityFilter`.
  - `app.schemas.document`: `SourceDocumentResponse`, `DocumentChunkResponse`.
  - `app.schemas.eligibility`: `RuleResultSchema`, `EligibilityResultSchema`, `EligibilityCheckRequest`.
- **Alembic Migrations**:
  - `alembic.ini`, `migrations/env.py`, `migrations/script.py.mako`.
  - `migrations/versions/001_initial_schema.py`: Initial schema creation for all 5 tables and indexes.
- **Testing & Verification**:
  - `backend/tests/unit/test_db_models.py`: Unit tests verifying model creation, relations, cascading deletes, and Pydantic validation using in-memory SQLite.
  - `scripts/test_db_connection.py`: Live smoke test script verifying container connectivity, table presence, and CRUD operations.

---

## Phase 3 — Opportunity Data & Seeding
**Date:** 2026-09-29
**Status:** ✅ Complete
**Commit:** `feat: implement opportunity API and data seeder`

### Architecture & Deliverables
- **API Endpoints**: Built full CRUD in `backend/app/api/v1/opportunities.py` (GET `/`, GET `/{id}`, POST `/`, PUT `/{id}`, DELETE `/{id}`).
- **Router Integration**: Registered `opportunities` router in `api/v1/router.py`.
- **Data Seeding**: Created `scripts/seed_opportunities.py` with 8 real-world scholarships (e.g., CSSS, AICTE Pragati, PMSS) mapped to the `Opportunity` ORM model.
- **Testing**: Added FastAPI `TestClient` integration tests in `backend/tests/integration/test_opportunity_api.py` for all CRUD operations using an in-memory SQLite database.

---

## Phase 4 — Document Ingestion Pipeline
**Date:** 2026-09-29
**Status:** ✅ Complete
**Commit:** `feat: implement document ingestion pipeline`

### Architecture & Deliverables
- **Ingestion Core**:
  - `loader.py`: Uses `PyPDFLoader` to extract raw text and metadata from PDF files.
  - `cleaner.py`: Normalizes text and fixes formatting issues.
  - `chunker.py`: Uses LangChain's `RecursiveCharacterTextSplitter` to create token-optimized chunks with overlaps.
- **API Endpoints**: Built `backend/app/api/v1/documents.py` (POST `/upload`, GET `/`, GET `/{id}`, GET `/{id}/chunks`) with FastAPI BackgroundTasks for asynchronous processing.
- **Router Integration**: Registered `documents` router in `api/v1/router.py`.
- **Testing**: Added `TestClient` integration tests generating dummy PDFs dynamically using `reportlab`.
- **Configuration**: Updated `requirements.txt` to include `langchain-community`, `langchain-text-splitters`, and `pypdf`.

---

## Phase 5 — Semantic Search & Embeddings
**Date:** 2026-09-29
**Status:** ✅ Complete
**Commit:** `feat: implement semantic embeddings using pgvector`

### Architecture & Deliverables
- **Database**: Updated `DocumentChunk` schema to store 384-dimensional `pgvector` embeddings (`embedding = Vector(384)`).
- **Embedding Engine**: Implemented `LocalEmbedder` in `backend/app/retrieval/embedder.py` using `langchain-huggingface` and the `BAAI/bge-small-en-v1.5` model loaded locally (fully offline).
- **Search Engine**: Built `SemanticSearcher` using the pgvector cosine distance operator `<=>` to rank document chunks.
- **Pipeline Integration**: Modified the background ingestion pipeline in `documents.py` to seamlessly embed new chunks directly into PostgreSQL.
- **API Endpoints**: Added `GET /api/v1/search/semantic`.

---

## Phase 6 — Keyword Search & Hybrid Retrieval
**Date:** 2026-09-29
**Status:** ✅ Complete
**Commit:** `feat: implement bm25 and hybrid rrf retrieval`

### Architecture & Deliverables
- **Keyword Engine**: Implemented `KeywordSearcher` in `backend/app/retrieval/keyword_search.py` using `rank_bm25`. Uses a singleton pattern to cache the tokenized corpus in-memory for speed.
- **Hybrid Fusion Engine**: Implemented `HybridSearcher` in `backend/app/retrieval/hybrid_search.py` combining Semantic and Keyword engine results using the Reciprocal Rank Fusion (RRF) algorithm.
- **Pipeline Integration**: Added a post-processing hook in the document ingestion pipeline to trigger an automatic `KeywordSearcher().refresh()` to keep the BM25 index up-to-date.
- **API Endpoints**: Added `GET /api/v1/search/keyword` and `GET /api/v1/search/hybrid`.
- **Testing**: Complete integration testing in `backend/tests/integration/test_hybrid_search.py` verifying RRF math and API outputs.

---

## Phase 7 — Student Profile Management
**Date:** 2026-09-29
**Status:** ✅ Complete
**Commit:** `feat: implement student profile management API`

### Architecture & Deliverables
- **API Endpoints**: Built full CRUD in `backend/app/api/v1/students.py` for `Student` entities (GET `/`, GET `/{id}`, POST `/`, PUT `/{id}`, DELETE `/{id}`).
- **Router Integration**: Registered `students` router in `api/v1/router.py`.
- **Data Seeding**: Created `scripts/seed_students.py` to inject diverse, realistic mock student profiles into the database for testing the eligibility engine.
- **Testing**: Added isolated FastAPI `TestClient` integration tests in `backend/tests/integration/test_student_api.py`.

---

*Next: Phase 8 — Eligibility Engine (Deterministic Rules)*
