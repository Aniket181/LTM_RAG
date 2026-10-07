#!/usr/bin/env python
"""
scripts/reembed_documents.py

Phase B — Backfill NULL Embeddings
====================================
Finds all document_chunks where embedding IS NULL in PostgreSQL and
generates + persists 384-dimensional BGE embeddings using the existing
LocalEmbedder implementation.

Safety guarantees:
  - Idempotent: running twice is safe (finds 0 chunks the second time).
  - No chunks are created, deleted, or text-modified.
  - Each chunk is committed individually with rollback on failure.
  - Smoke-test of the BGE model is performed before any DB writes.
  - Embedding validation: dimension == 384, no NaN, no Inf.

Usage (run from the project root):
    cd C:\\Users\\T10007\\Desktop\\Ltm_projects\\RAG
    venvrag\\Scripts\\activate
    python scripts/reembed_documents.py
"""

import sys
import os
import math
import logging

# -----------------------------------------------------------------------
# Path setup: add 'backend/' so that 'app.*' imports work correctly.
# -----------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# -----------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("reembed")


def validate_embedding(embedding, chunk_id: str) -> str | None:
    """
    Validate that the generated embedding is sane.
    Returns None on success, or an error string describing the problem.
    """
    if not isinstance(embedding, (list, tuple)):
        return f"Not a list/tuple (got {type(embedding).__name__})"

    if len(embedding) != 384:
        return f"Wrong dimension: expected 384, got {len(embedding)}"

    for i, val in enumerate(embedding):
        if math.isnan(val):
            return f"NaN at index {i}"
        if math.isinf(val):
            return f"Inf at index {i}"

    return None  # Valid


def run():
    # -----------------------------------------------------------------------
    # 1. Load config and session
    # -----------------------------------------------------------------------
    logger.info("Loading application configuration...")
    from app.core.config import settings

    logger.info(f"Database: {settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}")
    logger.info(f"Embedding model: {settings.embedding_model}")
    logger.info(f"Embedding device: {settings.embedding_device}")

    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # -----------------------------------------------------------------------
    # 2. Load the existing LocalEmbedder (singleton — uses BGE model)
    # -----------------------------------------------------------------------
    logger.info("Loading LocalEmbedder (BGE model)...")
    from app.retrieval.embedder import LocalEmbedder

    embedder = LocalEmbedder()
    logger.info("BGE model loaded successfully.")

    # -----------------------------------------------------------------------
    # 3. Smoke test: embed one small string before touching the DB
    # -----------------------------------------------------------------------
    logger.info("Running smoke test on the embedding model...")
    test_text = "This is a smoke test for the embedding model."
    test_embedding = embedder.embed_documents([test_text])[0]

    smoke_error = validate_embedding(test_embedding, chunk_id="smoke_test")
    if smoke_error:
        logger.error(f"SMOKE TEST FAILED: {smoke_error}")
        logger.error("Aborting — no database writes will be made.")
        sys.exit(1)

    logger.info(f"Smoke test PASSED — embedding dim={len(test_embedding)}, first_3={test_embedding[:3]}")

    # -----------------------------------------------------------------------
    # 4. Query all chunks with NULL embeddings
    # -----------------------------------------------------------------------
    from app.models.document import DocumentChunk

    db = SessionLocal()
    try:
        null_chunks = (
            db.query(DocumentChunk)
            .filter(DocumentChunk.embedding == None)  # noqa: E711 — SQLAlchemy requires ==
            .order_by(DocumentChunk.chunk_index)
            .all()
        )
    except Exception as e:
        db.close()
        logger.error(f"Failed to query database: {e}")
        sys.exit(1)

    total = len(null_chunks)
    logger.info(f"\nFound {total} chunk(s) requiring embeddings.")

    if total == 0:
        logger.info("Nothing to do. All chunks already have embeddings.")
        db.close()
        return

    # -----------------------------------------------------------------------
    # 5. Embed and persist each chunk individually (with per-chunk rollback)
    # -----------------------------------------------------------------------
    succeeded = 0
    failed = 0
    skipped = 0

    for idx, chunk in enumerate(null_chunks, start=1):
        chunk_id = str(chunk.id)
        progress = f"{idx}/{total}"

        if not chunk.content or not chunk.content.strip():
            logger.warning(f"  [{progress}] Chunk {chunk_id} — SKIPPED (empty content)")
            skipped += 1
            continue

        logger.info(f"  [{progress}] Embedding chunk {chunk_id} (page={chunk.page_number}, idx={chunk.chunk_index})...")

        try:
            # Generate embedding for this single chunk
            embeddings = embedder.embed_documents([chunk.content])

            if not embeddings or len(embeddings) == 0:
                raise ValueError("Embedder returned an empty list")

            embedding = embeddings[0]

            # Validate
            error = validate_embedding(embedding, chunk_id)
            if error:
                raise ValueError(f"Embedding validation failed: {error}")

            # Persist using a nested savepoint-style approach:
            # Load the chunk fresh from the current session, update, and commit.
            chunk.embedding = embedding
            db.add(chunk)
            db.commit()

            logger.info(f"  [{progress}] ✓ Saved (dim={len(embedding)})")
            succeeded += 1

        except Exception as e:
            db.rollback()
            logger.error(f"  [{progress}] ✗ FAILED for chunk {chunk_id}: {e}")
            failed += 1
            # Reload the session state after rollback to continue safely
            db.expire_all()

    db.close()

    # -----------------------------------------------------------------------
    # 6. Final summary
    # -----------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("PHASE B — EMBEDDING BACKFILL COMPLETE")
    print("=" * 60)
    print(f"  Total chunks processed : {total}")
    print(f"  Successfully embedded  : {succeeded}")
    print(f"  Failed                 : {failed}")
    print(f"  Skipped (empty text)   : {skipped}")
    print(f"  BGE model              : {settings.embedding_model}")
    print(f"  Embedding dimension    : 384")
    print("=" * 60)

    if failed > 0:
        logger.warning(f"{failed} chunk(s) failed to embed. Check the logs above for details.")
        sys.exit(1)

    # -----------------------------------------------------------------------
    # 7. Post-run database verification
    # -----------------------------------------------------------------------
    logger.info("\nRunning post-run database verification...")

    from sqlalchemy import text

    verify_engine = create_engine(settings.database_url, pool_pre_ping=True)
    with verify_engine.connect() as conn:
        total_chunks = conn.execute(text("SELECT COUNT(*) FROM document_chunks")).scalar()
        not_null = conn.execute(
            text("SELECT COUNT(*) FROM document_chunks WHERE embedding IS NOT NULL")
        ).scalar()
        null_remaining = conn.execute(
            text("SELECT COUNT(*) FROM document_chunks WHERE embedding IS NULL")
        ).scalar()

        # Verify dimension = 384 on a sample row
        sample = conn.execute(
            text("SELECT array_length(embedding::real[], 1) FROM document_chunks WHERE embedding IS NOT NULL LIMIT 1")
        ).scalar()

    print("\n--- DATABASE VERIFICATION ---")
    print(f"  Total document_chunks          : {total_chunks}")
    print(f"  embedding IS NOT NULL          : {not_null}")
    print(f"  embedding IS NULL              : {null_remaining}")
    print(f"  Sample embedding dimension     : {sample}")
    print("----------------------------")

    if null_remaining > 0:
        logger.warning(f"WARNING: {null_remaining} chunks still have NULL embeddings after backfill!")
    else:
        logger.info("✓ All chunks now have embeddings.")

    if sample != 384:
        logger.error(f"ERROR: Expected embedding dimension 384, got {sample}")
    else:
        logger.info(f"✓ Embedding dimension verified: {sample}")


if __name__ == "__main__":
    run()
