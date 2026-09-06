# RAG-Based Student Education Opportunity and Scholarship Eligibility Intelligence System

> **Final Year Academic Project** | Python · FastAPI · PostgreSQL · LangChain · Sentence Transformers · Next.js

---

## Problem Statement

Students — especially those from underrepresented or economically disadvantaged backgrounds — are often unaware of scholarships, fellowships, and educational opportunities they qualify for. Existing discovery mechanisms are scattered across dozens of portals, lack personalization, and provide no eligibility guidance.

This system solves this by combining:
- **Retrieval-Augmented Generation (RAG)** for grounded, cited answers
- **Hybrid Retrieval** (semantic + keyword + metadata filtering) for precise results
- **Deterministic Eligibility Engine** for reliable, explainable eligibility decisions
- **Opportunity Ranking** using a transparent multi-factor scoring approach

---

## Features

| Feature | Status |
|---------|--------|
| Student profile management | 🔄 Phase 7 |
| Structured eligibility evaluation | 🔄 Phase 8 |
| Semantic search (vector similarity) | 🔄 Phase 5 |
| Keyword search (BM25) | 🔄 Phase 6 |
| Hybrid retrieval + reranking | 🔄 Phase 6 |
| Opportunity ranking | 🔄 Phase 9 |
| RAG-based grounded Q&A | 🔄 Phase 10 |
| Source attribution / provenance | 🔄 Phase 10 |
| Student dashboard (frontend) | 🔄 Phase 12 |
| Evaluation framework | 🔄 Phase 13 |
| Docker deployment | 🔄 Phase 14 |

✅ Complete | 🔄 Planned | ⚠️ In Progress

---

## Architecture

```
Frontend (Next.js)
      │
      ▼
FastAPI REST API (/api/v1/)
      │
      ├── Student Profile Service
      ├── Eligibility Engine (Deterministic Rules)
      └── RAG Engine
              │
              ├── Semantic Retrieval (pgvector)
              ├── Keyword Retrieval (BM25)
              ├── Metadata Filtering
              └── LLM Generator (Grounded)
                      │
              PostgreSQL + ChromaDB/pgvector
```

See [`docs/architecture.md`](docs/architecture.md) for the full system diagram.

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Backend Framework | FastAPI 0.141+ |
| Language | Python 3.11 |
| ORM | SQLAlchemy 2.0 |
| Migrations | Alembic |
| Database | PostgreSQL + pgvector |
| Vector Store (dev) | ChromaDB |
| Embeddings | sentence-transformers (`BAAI/bge-small-en-v1.5`) |
| AI Framework | LangChain |
| Keyword Search | BM25 (rank_bm25) |
| PDF Processing | pypdf |
| Validation | Pydantic v2 |
| Testing | pytest + httpx |
| Frontend | Next.js 14 |
| Containerization | Docker + docker-compose |

---

## Project Structure

```
RAG/
├── backend/
│   ├── app/
│   │   ├── main.py          ← FastAPI app factory
│   │   ├── api/v1/          ← REST endpoints
│   │   ├── core/            ← config, logging, exceptions
│   │   ├── db/              ← SQLAlchemy setup
│   │   ├── models/          ← ORM models
│   │   ├── schemas/         ← Pydantic schemas
│   │   ├── eligibility/     ← Deterministic rule engine
│   │   ├── rag/             ← RAG pipeline
│   │   ├── retrieval/       ← Hybrid retrieval
│   │   ├── recommendations/ ← Opportunity ranker
│   │   └── ingestion/       ← Document ingestion
│   └── tests/
├── frontend/                ← Next.js application
├── data/
│   ├── raw/                 ← Source PDFs
│   ├── processed/           ← Cleaned text/chunks
│   └── sample/              ← Development sample data
├── scripts/                 ← Seed, ingest, evaluation
├── docs/                    ← Architecture and API docs
├── .env.example             ← Environment variable template
└── requirements.txt
```

---

## Installation

### Prerequisites
- Python 3.11+
- PostgreSQL 14+ (with pgvector extension for production)
- Node.js 18+ (for frontend)
- Git

### 1. Clone the repository
```bash
git clone https://github.com/Aniket181/RAG.git
cd RAG
```

### 2. Create and activate virtual environment
```bash
python -m venv venvrag
# Windows:
venvrag\Scripts\activate
# Linux/macOS:
source venvrag/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
cp .env.example .env
# Edit .env with your database credentials and API keys
```

---

## Environment Variables

See [`.env.example`](.env.example) for full documentation.

Key variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_USER` | Database username | `postgres` |
| `POSTGRES_PASSWORD` | Database password | *(required)* |
| `POSTGRES_DB` | Database name | `rag_scholarship_db` |
| `LLM_PROVIDER` | LLM backend (`mock`/`openai`/`google`) | `mock` |
| `EMBEDDING_MODEL` | Sentence transformer model | `BAAI/bge-small-en-v1.5` |
| `VECTOR_STORE_TYPE` | Vector backend (`chromadb`/`pgvector`) | `chromadb` |

---

## Running the Backend

```bash
# From the backend/ directory with venv active:
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API documentation available at: http://localhost:8000/docs

Health check: http://localhost:8000/api/v1/health

---

## Running Tests

```bash
cd backend
python -m pytest tests/ -v
```

---

## Development Phases

| Phase | Description | Status |
|-------|-------------|--------|
| 0 | Project Audit & Planning | ✅ Complete |
| 1 | Project Foundation | ✅ Complete |
| 2 | Database & Core Models | 🔄 Next |
| 3–15 | See `docs/development-log.md` | ⏳ Planned |

---

## Important Disclaimer

> All scholarship and educational opportunity information in this system is sourced from official government and institutional portals. Eligibility criteria, deadlines, and benefit amounts change regularly. **Always verify information from the official source before submitting any application.** This system provides decision support, not official eligibility determination.

---

## License

Academic project — for educational and research purposes.

---

## Author

Aniket | Final Year Project | 2026
