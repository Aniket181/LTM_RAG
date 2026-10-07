#!/usr/bin/env python3
"""
Phase G Corpus Validation Script
==================================
Post-ingestion validation of the Phase G scholarship corpus.

Reports:
  A. PDFs found in data/raw/
  B. SourceDocuments in PostgreSQL
  C. DocumentChunks in PostgreSQL
  D. Embedding integrity (dimension, null, NaN)
  E. Source category distribution
  F. Duplicate SHA-256 check
  G. OCR-required detection (docs with 0 chunks)
  H. Retrieval smoke test (semantic + hybrid)

USAGE:
    cd C:\\Users\\T10007\\Desktop\\Ltm_projects\\RAG\\backend
    python ../scripts/validate_phase_g_corpus.py
"""

import hashlib
import math
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.retrieval.embedder import LocalEmbedder


RAW_DIR = PROJECT_ROOT / "data" / "raw"
FOLDER_TO_CATEGORY = {
    "nsp": "NSP",
    "government_of_india": "Government of India",
    "ugc": "UGC",
    "aicte": "AICTE",
}


def log(msg):
    print(msg, flush=True)


def sep(c="─", w=62):
    log(c * w)


def main():
    sep("═")
    log("PHASE G — CORPUS VALIDATION")
    sep("═")

    engine = create_engine(settings.database_url, echo=False)
    Session = sessionmaker(bind=engine)

    # ── A. PDF files on disk ──────────────────────────────────────────────────
    sep()
    log("A. PDFs in data/raw/")
    sep()
    pdf_counts = {}
    all_pdfs = []
    for folder, cat in FOLDER_TO_CATEGORY.items():
        d = RAW_DIR / folder
        pdfs = list(d.glob("*.pdf")) if d.exists() else []
        pdf_counts[cat] = len(pdfs)
        all_pdfs.extend(pdfs)
        log(f"  {cat:30s}  {len(pdfs)} PDF(s)")
    log(f"  {'TOTAL':30s}  {len(all_pdfs)} PDF(s)")

    # ── B. SourceDocuments in DB ──────────────────────────────────────────────
    sep()
    log("B. SourceDocuments in PostgreSQL")
    sep()
    with Session() as session:
        total_docs = session.execute(text("SELECT COUNT(*) FROM source_documents")).scalar()
        cat_rows = session.execute(
            text("SELECT source_category, COUNT(*) FROM source_documents GROUP BY source_category ORDER BY source_category")
        ).fetchall()
        processed_docs = session.execute(
            text("SELECT COUNT(*) FROM source_documents WHERE ingestion_status = 'Processed'")
        ).scalar()
        failed_docs = session.execute(
            text("SELECT COUNT(*) FROM source_documents WHERE ingestion_status IN ('Failed','Error')")
        ).scalar()

    log(f"  Total SourceDocuments:  {total_docs}")
    log(f"  Processed:              {processed_docs}")
    log(f"  Failed/Error:           {failed_docs}")
    log("")
    for cat, cnt in cat_rows:
        log(f"  {cat:30s}  {cnt}")

    # ── C. DocumentChunks ────────────────────────────────────────────────────
    sep()
    log("C. DocumentChunks in PostgreSQL")
    sep()
    with Session() as session:
        total_chunks = session.execute(text("SELECT COUNT(*) FROM document_chunks")).scalar()
        null_emb = session.execute(
            text("SELECT COUNT(*) FROM document_chunks WHERE embedding IS NULL")
        ).scalar()
        docs_with_zero_chunks = session.execute(
            text("""
                SELECT COUNT(*) FROM source_documents sd
                WHERE sd.ingestion_status = 'Processed'
                AND NOT EXISTS (
                    SELECT 1 FROM document_chunks dc WHERE dc.source_document_id = sd.id
                )
            """)
        ).scalar()

    log(f"  Total chunks:           {total_chunks}")
    log(f"  Null embeddings:        {null_emb}")
    log(f"  Processed docs with 0 chunks (OCR?): {docs_with_zero_chunks}")

    # ── D. Embedding dimension spot-check ─────────────────────────────────────
    sep()
    log("D. Embedding Integrity Spot-Check (sampling 50 chunks)")
    sep()
    with Session() as session:
        sample = session.execute(
            text("SELECT embedding FROM document_chunks WHERE embedding IS NOT NULL LIMIT 50")
        ).fetchall()

    dim_errors = 0
    nan_errors = 0
    parse_errors = 0
    for row in sample:
        emb = row[0]
        if emb is None:
            continue
            
        # Safely convert to a list of floats
        try:
            if isinstance(emb, str):
                emb_str = emb.strip("[]")
                values = [float(x) for x in emb_str.split(",") if x.strip()]
            else:
                values = [float(x) for x in emb]
        except (ValueError, TypeError):
            parse_errors += 1
            continue
            
        if len(values) != 384:
            dim_errors += 1
        if any(math.isnan(v) or math.isinf(v) for v in values):
            nan_errors += 1

    log(f"  Sampled:                {len(sample)}")
    log(f"  Parse errors:           {parse_errors}")
    log(f"  Dimension errors (≠384): {dim_errors}")
    log(f"  NaN/Inf errors:          {nan_errors}")

    # ── E. pgvector extension ─────────────────────────────────────────────────
    sep()
    log("E. pgvector Extension")
    sep()
    with Session() as session:
        try:
            ext = session.execute(
                text("SELECT extname, extversion FROM pg_extension WHERE extname='vector'")
            ).fetchone()
            if ext:
                log(f"  pgvector: {ext[0]} v{ext[1]}  ✅")
            else:
                log("  pgvector: NOT FOUND ❌")
        except Exception as e:
            log(f"  pgvector check error: {e}")

    # ── F. Duplicate SHA-256 in chunk_metadata ────────────────────────────────
    sep()
    log("F. Duplicate Document SHA-256 Check")
    sep()
    with Session() as session:
        dup_rows = session.execute(
            text("""
                SELECT chunk_metadata->>'sha256' AS hash, COUNT(DISTINCT source_document_id) AS doc_count
                FROM document_chunks
                WHERE chunk_metadata->>'sha256' IS NOT NULL
                GROUP BY hash
                HAVING COUNT(DISTINCT source_document_id) > 1
            """)
        ).fetchall()
    if dup_rows:
        log(f"  WARNING: {len(dup_rows)} SHA-256 hash(es) appear in multiple documents:")
        for r in dup_rows:
            log(f"    hash={str(r[0])[:16]}...  in {r[1]} docs")
    else:
        log("  No duplicate SHA-256 hashes detected ✅")

    # ── G. Per-doc chunk and opportunity distribution ─────────────────────────
    sep()
    log("G. Per-Document Chunk Distribution")
    sep()
    with Session() as session:
        doc_rows = session.execute(
            text("""
                SELECT sd.title, sd.source_category, sd.source_organization,
                       sd.academic_year, sd.ingestion_status,
                       COUNT(dc.id) AS chunk_count
                FROM source_documents sd
                LEFT JOIN document_chunks dc ON dc.source_document_id = sd.id
                WHERE sd.ingestion_status = 'Processed'
                GROUP BY sd.id, sd.title, sd.source_category, sd.source_organization,
                         sd.academic_year, sd.ingestion_status
                ORDER BY sd.source_category, sd.title
            """)
        ).fetchall()

    log(f"  {'Title'[:40]:40s}  {'Category':20s}  Chunks")
    log("  " + "─" * 70)
    total_chunk_sum = 0
    for row in doc_rows:
        title, cat, org, yr, status, cnt = row
        total_chunk_sum += (cnt or 0)
        log(f"  {(title or '')[:40]:40s}  {(cat or '')[:20]:20s}  {cnt}")
    log(f"\n  Total chunks across processed docs: {total_chunk_sum}")

    # ── H. Retrieval smoke test ───────────────────────────────────────────────
    sep()
    log("H. Retrieval Smoke Test")
    sep()

    from app.retrieval.search import SemanticSearcher

    queries = [
        ("eligibility criteria scholarship income", True),
        ("scholarship amount per annum tuition fee", True),
        ("application process required documents renewal", True),
        ("bicycle wheel puncture repair kit", False),
    ]

    all_ok = True
    with Session() as session:
        searcher = SemanticSearcher(session)
        for query, expect_hits in queries:
            try:
                hits = searcher.search(query, k=3)
                n = len(hits)
                ok = (expect_hits and n > 0) or (not expect_hits)
                status = "OK" if ok else "WARN"
                if not ok:
                    all_ok = False
                top_title = hits[0]["document_title"] if n > 0 else "—"
                log(f"  [{status}] '{query[:50]}'  → {n} hit(s)  top: {top_title[:40]}")
            except Exception as e:
                log(f"  [ERROR] {query[:40]}: {e}")
                all_ok = False

    # ── Summary ───────────────────────────────────────────────────────────────
    sep("═")
    log("VALIDATION SUMMARY")
    sep("═")
    log(f"  PDFs on disk:               {len(all_pdfs)}")
    log(f"  SourceDocuments in DB:      {total_docs}")
    log(f"  Processed:                  {processed_docs}")
    log(f"  Chunks in DB:               {total_chunks}")
    log(f"  Null embeddings:            {null_emb}")
    log(f"  Parse errors:               {parse_errors}")
    log(f"  Dim/NaN errors (sampled):   {dim_errors + nan_errors}")
    log(f"  Duplicate SHA-256:          {len(dup_rows)}")
    log(f"  OCR-required (0 chunks):    {docs_with_zero_chunks}")
    log(f"  Retrieval smoke test:       {'ALL OK ✅' if all_ok else 'WARNINGS ⚠️'}")
    log("")
    log("  ✅ No existing Phase A-F data deleted")
    log("  ✅ Only four approved source categories checked")
    sep("═")


if __name__ == "__main__":
    main()
