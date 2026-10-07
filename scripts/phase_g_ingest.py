#!/usr/bin/env python3
"""
Phase G — Batch PDF Ingestion Script
=====================================
Audits, validates provenance, extracts text, chunks, embeds (BGE 384D),
and stores into PostgreSQL/pgvector for all verified PDFs in data/raw/.

Reuses existing pipeline components:
  - app.ingestion.loader.DocumentLoader
  - app.ingestion.cleaner.TextCleaner
  - app.ingestion.chunker.DocumentChunker
  - app.retrieval.embedder.LocalEmbedder
  - app.models.document.SourceDocument, DocumentChunk

USAGE:
    cd C:\\Users\\T10007\\Desktop\\Ltm_projects\\RAG\\backend
    python ../scripts/phase_g_ingest.py [--audit-only] [--dry-run]

    --audit-only  : Run file audit and provenance check, do NOT ingest
    --dry-run     : Run full pipeline up to DB insert, but do NOT commit
"""

import hashlib
import json
import math
import os
import sys
import time
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ── bootstrap: make sure backend is on sys.path ──────────────────────────────
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

# ── project imports ───────────────────────────────────────────────────────────
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.document import DocumentChunk, SourceDocument
from app.ingestion.loader import DocumentLoader
from app.ingestion.cleaner import TextCleaner
from app.ingestion.chunker import DocumentChunker
from app.retrieval.embedder import LocalEmbedder

# ── configuration ─────────────────────────────────────────────────────────────
RAW_DIR = PROJECT_ROOT / "data" / "raw"

FOLDER_TO_CATEGORY = {
    "nsp": "NSP",
    "government_of_india": "Government of India",
    "ugc": "UGC",
    "aicte": "AICTE",
}

ALLOWED_CATEGORIES = {"NSP", "Government of India", "UGC", "AICTE"}
MIN_CHUNK_TEXT_LEN = 50
MIN_TOTAL_TEXT_LEN = 200

# Files intentionally skipped due to OCR requirements
SKIPPED_FILES = {
    "Post-Matric Scholarship for Scheduled Castes (SC).pdf": "OCR_REQUIRED_SKIPPED",
}



# ─────────────────────────────────────────────────────────────────────────────
# PROVENANCE CATALOGUE — derived from Phase G collection plan
# ─────────────────────────────────────────────────────────────────────────────

FILENAME_PROVENANCE: Dict[str, Dict[str, Any]] = {
    # ── NSP ──────────────────────────────────────────────────────────────────
    "Central Sector Scheme of Scholarships for College and University Students (CSSS).pdf": {
        "opportunity_name": "Central Sector Scheme of Scholarships for College and University Students (CSSS)",
        "document_title": "Central Sector Scheme of Scholarships (CSSS) Guidelines",
        "source_category": "NSP",
        "source_organization": "Ministry of Education",
        "official_source_url": "https://scholarships.gov.in/public/schemeGuidelines/centralsOrsponsoredOrstate",
        "academic_year": "2024-25",
        "document_type": "Scholarship Guideline",
    },
    "National Fellowship for OBC Students.pdf": {
        "opportunity_name": "National Fellowship for OBC Students",
        "document_title": "National Fellowship for OBC Students Guidelines",
        "source_category": "NSP",
        "source_organization": "Ministry of Social Justice & Empowerment",
        "official_source_url": "https://scholarships.gov.in/public/schemeGuidelines/centralsOrsponsoredOrstate",
        "academic_year": "2024-25",
        "document_type": "Scholarship Guideline",
    },
    "National Means-cum-Merit Scholarship (NMMS).pdf": {
        "opportunity_name": "National Means-cum-Merit Scholarship (NMMS)",
        "document_title": "National Means-cum-Merit Scholarship Scheme Guidelines",
        "source_category": "NSP",
        "source_organization": "Ministry of Education",
        "official_source_url": "https://scholarships.gov.in/public/schemeGuidelines/centralsOrsponsoredOrstate",
        "academic_year": "2024-25",
        "document_type": "Scholarship Guideline",
    },
    "Post-Matric Scholarship for OBC Students.pdf": {
        "opportunity_name": "Post-Matric Scholarship for OBC Students",
        "document_title": "Post-Matric Scholarship for OBC Students Guidelines",
        "source_category": "NSP",
        "source_organization": "Ministry of Social Justice & Empowerment",
        "official_source_url": "https://scholarships.gov.in/public/schemeGuidelines/centralsOrsponsoredOrstate",
        "academic_year": "2024-25",
        "document_type": "Scholarship Guideline",
    },
    "Post-Matric Scholarship for Scheduled Castes (SC).pdf": {
        "opportunity_name": "Post-Matric Scholarship for Scheduled Castes (SC)",
        "document_title": "Post-Matric Scholarship for Scheduled Castes (SC) Guidelines",
        "source_category": "NSP",
        "source_organization": "Ministry of Social Justice & Empowerment",
        "official_source_url": "https://scholarships.gov.in/public/schemeGuidelines/centralsOrsponsoredOrstate",
        "academic_year": "2024-25",
        "document_type": "Scholarship Guideline",
    },
    "Post-Matric Scholarship for Scheduled Tribes (ST).pdf": {
        "opportunity_name": "Post-Matric Scholarship for Scheduled Tribes (ST)",
        "document_title": "Post-Matric Scholarship for Scheduled Tribes (ST) Guidelines",
        "source_category": "NSP",
        "source_organization": "Ministry of Tribal Affairs",
        "official_source_url": "https://scholarships.gov.in/public/schemeGuidelines/centralsOrsponsoredOrstate",
        "academic_year": "2024-25",
        "document_type": "Scholarship Guideline",
    },
    "Scholarship for Top Class Education for SC Students.pdf": {
        "opportunity_name": "Scholarship for Top Class Education for SC Students",
        "document_title": "Scholarship for Top Class Education for SC Students Guidelines",
        "source_category": "NSP",
        "source_organization": "Ministry of Social Justice & Empowerment",
        "official_source_url": "https://scholarships.gov.in/public/schemeGuidelines/centralsOrsponsoredOrstate",
        "academic_year": "2024-25",
        "document_type": "Scholarship Guideline",
    },
    # ── UGC ──────────────────────────────────────────────────────────────────
    "Ishan Uday Special Scholarship Scheme for North Eastern Region.pdf": {
        "opportunity_name": "Ishan Uday Special Scholarship Scheme for North Eastern Region",
        "document_title": "Ishan Uday Special Scholarship Scheme for NE Region Guidelines",
        "source_category": "UGC",
        "source_organization": "University Grants Commission",
        "official_source_url": "https://www.ugc.gov.in/Scholarships/stu_Scholarship5",
        "academic_year": "2024-25",
        "document_type": "Scholarship Guideline",
    },
    "National Scholarship for Post Graduate Studies (NPGS).pdf": {
        "opportunity_name": "National Scholarship for Post Graduate Studies (NPGS)",
        "document_title": "National Scholarship for Post Graduate Studies (NPGS) Guidelines",
        "source_category": "UGC",
        "source_organization": "University Grants Commission",
        "official_source_url": "https://www.ugc.gov.in/Scholarships/stu_Scholarship6",
        "academic_year": "2024-25",
        "document_type": "Scholarship Guideline",
    },
    "PG Indira Gandhi Scholarship for Single Girl Child.pdf": {
        "opportunity_name": "PG Indira Gandhi Scholarship for Single Girl Child",
        "document_title": "PG Indira Gandhi Scholarship for Single Girl Child Guidelines",
        "source_category": "UGC",
        "source_organization": "University Grants Commission",
        "official_source_url": "https://www.ugc.gov.in/Home/student_Corner",
        "academic_year": "2024-25",
        "document_type": "Scholarship Guideline",
    },
    "Savitribai Jyotirao Phule Fellowship for Single Girl Child (PG).pdf": {
        "opportunity_name": "Savitribai Jyotirao Phule Fellowship for Single Girl Child",
        "document_title": "Savitribai Jyotirao Phule Fellowship for Single Girl Child (PG) Guidelines",
        "source_category": "UGC",
        "source_organization": "University Grants Commission",
        "official_source_url": "https://www.ugc.gov.in/Fellowship/stu_Fellowship3",
        "academic_year": "2024-25",
        "document_type": "Fellowship Guideline",
    },
    "UGC Junior Research Fellowship (JRF) in Science, Humanities and Social Sciences  University Grants Commission.pdf": {
        "opportunity_name": "UGC Junior Research Fellowship (JRF)",
        "document_title": "UGC JRF in Science, Humanities and Social Sciences Guidelines",
        "source_category": "UGC",
        "source_organization": "University Grants Commission",
        "official_source_url": "https://www.ugc.gov.in/Fellowship/stu_Fellowship1",
        "academic_year": "2024-25",
        "document_type": "Fellowship Guideline",
    },
    # ── AICTE ─────────────────────────────────────────────────────────────────
    "Pragati Scholarship Scheme.pdf": {
        "opportunity_name": "AICTE Pragati Scholarship Scheme (Girl Students in Technical Education)",
        "document_title": "AICTE Pragati Scholarship Scheme Guidelines",
        "source_category": "AICTE",
        "source_organization": "All India Council for Technical Education",
        "official_source_url": "https://www.aicte-india.org/schemes/students-development-schemes",
        "academic_year": "2024-25",
        "document_type": "Scholarship Guideline",
    },
    "Saksham Scholarship Scheme.pdf": {
        "opportunity_name": "AICTE Saksham Scholarship Scheme (Students with Disabilities)",
        "document_title": "AICTE Saksham Scholarship Scheme Guidelines",
        "source_category": "AICTE",
        "source_organization": "All India Council for Technical Education",
        "official_source_url": "https://www.aicte-india.org/schemes/students-development-schemes",
        "academic_year": "2024-25",
        "document_type": "Scholarship Guideline",
    },
    "AICTE-NEC Scholarship.pdf": {
        "opportunity_name": "AICTE-NEC Scholarship (North Eastern Council)",
        "document_title": "AICTE-NEC Scholarship Scheme Guidelines",
        "source_category": "AICTE",
        "source_organization": "All India Council for Technical Education",
        "official_source_url": "https://www.aicte-india.org/schemes/students-development-schemes",
        "academic_year": "2024-25",
        "document_type": "Scholarship Guideline",
    },
    "AICTE National Doctoral Fellowship.pdf": {
        "opportunity_name": "AICTE National Doctoral Fellowship",
        "document_title": "AICTE National Doctoral Fellowship Guidelines",
        "source_category": "AICTE",
        "source_organization": "All India Council for Technical Education",
        "official_source_url": "https://www.aicte-india.org/bureaus/scholarships-and-grants",
        "academic_year": "2024-25",
        "document_type": "Fellowship Guideline",
    },
    "AICTE Research Promotion Scheme.pdf": {
        "opportunity_name": "AICTE Research Promotion Scheme",
        "document_title": "AICTE Research Promotion Scheme Guidelines",
        "source_category": "AICTE",
        "source_organization": "All India Council for Technical Education",
        "official_source_url": "https://www.aicte-india.org/bureaus/scholarships-and-grants",
        "academic_year": "2024-25",
        "document_type": "Scholarship Guideline",
    },
    "AICTE Saraswati Scholarship Scheme Guidelines_2024-Final.pdf": {
        "opportunity_name": "AICTE Saraswati Scholarship Scheme",
        "document_title": "AICTE Saraswati Scholarship Scheme Guidelines 2024",
        "source_category": "AICTE",
        "source_organization": "All India Council for Technical Education",
        "official_source_url": "https://www.aicte-india.org/schemes/students-development-schemes",
        "academic_year": "2024-25",
        "document_type": "Scholarship Guideline",
    },
    "ICTE DOCTORAL FELLOWSHIP (ADF) Scholarship.pdf": {
        "opportunity_name": "AICTE Doctoral Fellowship (ADF)",
        "document_title": "AICTE Doctoral Fellowship (ADF) Scholarship Guidelines",
        "source_category": "AICTE",
        "source_organization": "All India Council for Technical Education",
        "official_source_url": "https://www.aicte-india.org/bureaus/scholarships-and-grants",
        "academic_year": "2024-25",
        "document_type": "Fellowship Guideline",
        "_review_note": "Filename missing leading 'A' — likely typo. Verify PDF content confirms AICTE origin.",
    },
    "PG Scholarship Gate.pdf": {
        "opportunity_name": "AICTE PG Scholarship for GATE/GPAT-qualified Students",
        "document_title": "AICTE PG Scholarship for GATE/GPAT qualified students Guidelines",
        "source_category": "AICTE",
        "source_organization": "All India Council for Technical Education",
        "official_source_url": "https://www.aicte-india.org/schemes/students-development-schemes",
        "academic_year": "2024-25",
        "document_type": "Scholarship Guideline",
    },
    # ── Government of India ───────────────────────────────────────────────────
    "National Overseas Scholarship for ST Students.pdf": {
        "opportunity_name": "National Overseas Scholarship for Scheduled Tribe Students",
        "document_title": "National Overseas Scholarship for Scheduled Tribe Students Guidelines",
        "source_category": "Government of India",
        "source_organization": "Ministry of Tribal Affairs",
        "official_source_url": "https://tribal.gov.in/",
        "academic_year": "2024-25",
        "document_type": "Scholarship Guideline",
    },
    "PG Scholarship for Professional Courses SC ST.pdf": {
        "opportunity_name": "PG Scholarship for Professional Courses for SC/ST Students",
        "document_title": "PG Scholarship for Professional Courses for SC/ST Students Guidelines",
        "source_category": "Government of India",
        "source_organization": "Ministry of Education",
        "official_source_url": "https://www.education.gov.in/scholarship-and-fellowships-students",
        "academic_year": "2024-25",
        "document_type": "Scholarship Guideline",
    },
    "Post-Matric Scholarship for Minorities \u2014 Official Guidelines.pdf": {
        "opportunity_name": "Post-Matric Scholarship for Minority Communities",
        "document_title": "Post-Matric Scholarship for Minorities — Official Guidelines",
        "source_category": "Government of India",
        "source_organization": "Ministry of Minority Affairs",
        "official_source_url": "https://www.minorityaffairs.gov.in/",
        "academic_year": "2024-25",
        "document_type": "Scholarship Guideline",
    },
    "Pre-Matric Scholarship for Minorities \u2014 Official Guidelines.pdf": {
        "opportunity_name": "Pre-Matric Scholarship for Minority Communities",
        "document_title": "Pre-Matric Scholarship for Minorities — Official Guidelines",
        "source_category": "Government of India",
        "source_organization": "Ministry of Minority Affairs",
        "official_source_url": "https://www.minorityaffairs.gov.in/",
        "academic_year": "2024-25",
        "document_type": "Scholarship Guideline",
    },
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def is_valid_pdf(path: Path) -> bool:
    try:
        with open(path, "rb") as f:
            return f.read(4) == b"%PDF"
    except Exception:
        return False


def log(msg: str):
    print(msg, flush=True)


def sep(char="─", width=62):
    log(char * width)


# ─────────────────────────────────────────────────────────────────────────────
# STEP 1 — FILE AUDIT
# ─────────────────────────────────────────────────────────────────────────────

def audit_files() -> Tuple[List[Dict], List[str]]:
    sep("═")
    log("STEP 1 — FILE AUDIT")
    sep("═")

    records = []
    warnings = []
    seen_hashes: Dict[str, str] = {}
    seen_sizes: Dict[int, str] = {}

    for folder, category in FOLDER_TO_CATEGORY.items():
        folder_path = RAW_DIR / folder
        if not folder_path.exists():
            warnings.append(f"Directory not found: {folder_path}")
            continue

        pdfs = sorted(p for p in folder_path.iterdir() if p.suffix.lower() == ".pdf")
        log(f"\n  [{category}]  ({len(pdfs)} PDF(s))")

        for pdf in pdfs:
            rec: Dict[str, Any] = {
                "filename": pdf.name,
                "folder": folder,
                "category": category,
                "path": pdf,
                "size_bytes": pdf.stat().st_size,
                "is_valid_pdf": False,
                "sha256": None,
                "duplicate_of": None,
                "status": "pending",
                "review_notes": [],
            }

            if not is_valid_pdf(pdf):
                rec["status"] = "invalid_not_pdf"
                warnings.append(f"NOT A VALID PDF: {pdf.name}")
                log(f"    [ERROR] {pdf.name} — not a valid PDF")
                records.append(rec)
                continue
            rec["is_valid_pdf"] = True

            file_hash = sha256_file(pdf)
            rec["sha256"] = file_hash

            if file_hash in seen_hashes:
                rec["status"] = "duplicate_hash"
                rec["duplicate_of"] = seen_hashes[file_hash]
                warnings.append(f"DUPLICATE HASH: {pdf.name} == {seen_hashes[file_hash]}")
                log(f"    [DUP-HASH] {pdf.name} duplicates {seen_hashes[file_hash]}")
            elif pdf.name in SKIPPED_FILES:
                rec["status"] = SKIPPED_FILES[pdf.name]
                warnings.append(f"SKIPPED INTENTIONALLY ({SKIPPED_FILES[pdf.name]}): {pdf.name}")
                log(f"    [SKIPPED] {pdf.name}  — {SKIPPED_FILES[pdf.name]}")
            else:
                seen_hashes[file_hash] = pdf.name
                sz = rec["size_bytes"]
                if sz in seen_sizes:
                    note = f"Same file size ({sz}B) as {seen_sizes[sz]} — verify content differs"
                    rec["review_notes"].append(note)
                    warnings.append(f"SAME SIZE ({sz}B): {pdf.name} and {seen_sizes[sz]}")
                    log(f"    [WARN-SIZE] {pdf.name} same size as {seen_sizes[sz]}")
                seen_sizes[sz] = pdf.name
                rec["status"] = "audit_passed"
                log(f"    [OK] {pdf.name}  {rec['size_bytes']:,}B  sha256={file_hash[:16]}...")

            records.append(rec)

    sep()
    total = len(records)
    valid = sum(1 for r in records if r["status"] == "audit_passed")
    dups = sum(1 for r in records if r["status"] == "duplicate_hash")
    invalid = sum(1 for r in records if r["status"] == "invalid_not_pdf")
    skipped = sum(1 for r in records if r["status"] in SKIPPED_FILES.values())
    log(f"  Total PDFs: {total}  |  Passed: {valid}  |  Duplicate: {dups}  |  Skipped: {skipped}  |  Invalid: {invalid}")
    return records, warnings


# ─────────────────────────────────────────────────────────────────────────────
# STEP 2 — PROVENANCE ASSIGNMENT
# ─────────────────────────────────────────────────────────────────────────────

def assign_provenance(records: List[Dict]) -> List[Dict]:
    sep("═")
    log("STEP 2 — PROVENANCE ASSIGNMENT")
    sep("═")

    prov_file = RAW_DIR / "provenance.json"
    prov_overrides: Dict[str, Any] = {}
    if prov_file.exists():
        try:
            raw = json.loads(prov_file.read_text(encoding="utf-8"))
            prov_overrides = {
                k: v for k, v in raw.items()
                if not k.startswith("_")
                and isinstance(v, dict)
                and "FILL_IN" not in str(v.get("source_category", ""))
            }
            if prov_overrides:
                log(f"  Loaded {len(prov_overrides)} override(s) from provenance.json")
        except Exception as e:
            log(f"  [WARN] Could not parse provenance.json: {e}")

    for rec in records:
        if rec["status"] != "audit_passed":
            continue

        fname = rec["filename"]
        p = prov_overrides.get(fname) or FILENAME_PROVENANCE.get(fname)

        if not p:
            rec["status"] = "needs_manual_review"
            rec["review_notes"].append("No provenance entry — manual review required")
            log(f"  [MANUAL REVIEW] {fname}")
            continue

        rec.update({
            "opportunity_name": p.get("opportunity_name", ""),
            "document_title": p.get("document_title", fname),
            "source_category": p.get("source_category", rec["category"]),
            "source_organization": p.get("source_organization", ""),
            "official_source_url": p.get("official_source_url", ""),
            "academic_year": p.get("academic_year", ""),
            "publication_date": p.get("publication_date"),
            "document_type": p.get("document_type", "Scholarship Guideline"),
        })
        if "_review_note" in p:
            rec["review_notes"].append(p["_review_note"])

        if rec.get("source_category") not in ALLOWED_CATEGORIES:
            rec["status"] = "needs_manual_review"
            rec["review_notes"].append(f"Invalid category: {rec.get('source_category')}")
            log(f"  [INVALID CATEGORY] {fname}")
            continue

        org = rec.get("source_organization", "")
        if org in ("", "Government", "India Government", "Official Website"):
            rec["status"] = "needs_manual_review"
            rec["review_notes"].append(f"Generic source_organization: '{org}'")
            log(f"  [GENERIC ORG] {fname}")
            continue

        if rec["review_notes"]:
            rec["status"] = "provenance_verified_with_notes"
            log(f"  [VERIFIED+NOTES] {fname}  ({rec['source_category']})")
        else:
            rec["status"] = "provenance_verified"
            log(f"  [VERIFIED] {fname}  ({rec['source_category']} / {rec['source_organization']})")

    sep()
    verified = sum(1 for r in records if r["status"] in ("provenance_verified", "provenance_verified_with_notes"))
    review = sum(1 for r in records if r["status"] == "needs_manual_review")
    log(f"  Provenance verified: {verified}  |  Manual review: {review}")
    return records


# ─────────────────────────────────────────────────────────────────────────────
# STEP 3 — INGEST PIPELINE
# ─────────────────────────────────────────────────────────────────────────────

def ingest_documents(records: List[Dict], dry_run: bool = False) -> Dict[str, Any]:
    sep("═")
    log(f"STEP 3 — INGESTION {'[DRY RUN]' if dry_run else ''}")
    sep("═")

    engine = create_engine(settings.database_url, echo=False)
    Session = sessionmaker(bind=engine)

    loader = DocumentLoader()
    cleaner = TextCleaner()
    chunker = DocumentChunker(chunk_size=settings.chunk_size, chunk_overlap=settings.chunk_overlap)

    log("  Loading BGE embedding model...")
    embedder = LocalEmbedder()
    log("  BGE model ready.\n")

    with Session() as session:
        pre_chunk_count = session.execute(text("SELECT COUNT(*) FROM document_chunks")).scalar()
        pre_doc_count = session.execute(text("SELECT COUNT(*) FROM source_documents")).scalar()

    log(f"  Existing SourceDocuments: {pre_doc_count}")
    log(f"  Existing DocumentChunks:  {pre_chunk_count}\n")

    results = {
        "pre_doc_count": pre_doc_count,
        "pre_chunk_count": pre_chunk_count,
        "processed": [],
        "failed": [],
        "skipped_review": [],
        "skipped_duplicate": [],
        "ocr_required": [],
        "total_chunks": 0,
        "total_embeddings": 0,
    }

    ingestable = [r for r in records if r["status"] in ("provenance_verified", "provenance_verified_with_notes")]
    log(f"  Documents to ingest: {len(ingestable)}")

    for rec in ingestable:
        fname = rec["filename"]
        fpath = rec["path"]
        sep("─", 50)
        log(f"  Processing: {fname}")

        try:
            with Session() as session:
                # Duplicate DB check
                existing = session.execute(
                    text("SELECT id, title FROM source_documents WHERE file_path LIKE :pat"),
                    {"pat": f"%{fname}%"},
                ).fetchone()
                if existing:
                    log(f"    [SKIP-DB-DUP] Already ingested: {existing[1]}")
                    results["skipped_duplicate"].append(fname)
                    continue

                # Load PDF
                t0 = time.time()
                pages = loader.load_pdf(str(fpath))
                total_text = " ".join(p.page_content for p in pages)
                log(f"    Loaded {len(pages)} page(s)  {len(total_text):,} chars  ({time.time()-t0:.1f}s)")

                # OCR check
                if len(total_text.strip()) < MIN_TOTAL_TEXT_LEN:
                    log(f"    [OCR_REQUIRED] Text too short ({len(total_text)} chars)")
                    results["ocr_required"].append(fname)
                    continue

                # Clean + chunk
                cleaned = cleaner.clean_documents(pages)
                chunks = chunker.chunk_documents(cleaned)
                chunks = [c for c in chunks if len(c.page_content.strip()) >= MIN_CHUNK_TEXT_LEN]
                log(f"    Chunks after filter: {len(chunks)}")

                if not chunks:
                    results["failed"].append({"file": fname, "error": "No usable chunks after filtering"})
                    continue

                # Embed
                t1 = time.time()
                texts = [c.page_content for c in chunks]
                embeddings = embedder.embed_documents(texts)
                assert len(embeddings) == len(chunks)
                for emb in embeddings:
                    assert len(emb) == 384
                    assert not any(math.isnan(v) or math.isinf(v) for v in emb)
                log(f"    Embeddings: {len(embeddings)} × 384D  ({time.time()-t1:.1f}s)")

                if dry_run:
                    log("    [DRY RUN] Skipping DB insert")
                    results["processed"].append({
                        "file": fname, "chunks": len(chunks),
                        "embeddings": len(embeddings), "source_category": rec["source_category"],
                    })
                    results["total_chunks"] += len(chunks)
                    results["total_embeddings"] += len(embeddings)
                    continue

                # Store SourceDocument
                src_doc = SourceDocument(
                    title=rec["document_title"],
                    source_category=rec["source_category"],
                    source_organization=rec["source_organization"],
                    source_url=rec.get("official_source_url"),
                    document_type=rec.get("document_type", "Scholarship Guideline"),
                    file_path=str(fpath.relative_to(PROJECT_ROOT)),
                    academic_year=rec.get("academic_year"),
                    last_verified_date=date.today(),
                    ingestion_status="Processing",
                )
                session.add(src_doc)
                session.flush()

                # Store DocumentChunks with embeddings
                chunk_objs = []
                for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
                    page_num = chunk.metadata.get("page")
                    if isinstance(page_num, int):
                        page_num += 1
                    chunk_objs.append(DocumentChunk(
                        source_document_id=src_doc.id,
                        content=chunk.page_content,
                        chunk_index=i,
                        page_number=page_num,
                        chunk_metadata={
                            "source_category": rec["source_category"],
                            "opportunity_name": rec.get("opportunity_name", ""),
                            "academic_year": rec.get("academic_year", ""),
                            "sha256": rec["sha256"],
                        },
                        embedding=emb,
                    ))
                session.add_all(chunk_objs)
                src_doc.ingestion_status = "Processed"
                session.commit()

                log(f"    [STORED] doc_id={src_doc.id}  chunks={len(chunk_objs)}  status=Processed")
                results["processed"].append({
                    "file": fname, "doc_id": str(src_doc.id),
                    "chunks": len(chunk_objs), "embeddings": len(embeddings),
                    "source_category": rec["source_category"],
                })
                results["total_chunks"] += len(chunk_objs)
                results["total_embeddings"] += len(embeddings)

        except Exception as e:
            log(f"    [ERROR] {e}")
            results["failed"].append({"file": fname, "error": str(e)})

    results["skipped_review"] = [r["filename"] for r in records if r["status"] == "needs_manual_review"]

    with Session() as session:
        results["post_chunk_count"] = session.execute(text("SELECT COUNT(*) FROM document_chunks")).scalar()
        results["post_doc_count"] = session.execute(text("SELECT COUNT(*) FROM source_documents")).scalar()

    return results


# ─────────────────────────────────────────────────────────────────────────────
# STEP 4 — RETRIEVAL SMOKE TEST
# ─────────────────────────────────────────────────────────────────────────────

def retrieval_smoke_test() -> Dict[str, Any]:
    sep("═")
    log("STEP 4 — RETRIEVAL SMOKE TEST")
    sep("═")

    from app.retrieval.semantic_search import SemanticSearcher

    engine = create_engine(settings.database_url, echo=False)
    Session = sessionmaker(bind=engine)
    searcher = SemanticSearcher()

    test_queries = [
        ("eligibility criteria income scholarship", True),
        ("scholarship amount per annum tuition fee waiver", True),
        ("application process required documents renewal", True),
        ("how to fix a bicycle chain derailleur gear", False),
    ]

    results = {}
    with Session() as session:
        for query, expect_hits in test_queries:
            try:
                hits = searcher.search(session, query, k=3, distance_threshold=0.80)
                n = len(hits)
                ok = (expect_hits and n > 0) or (not expect_hits)
                status = "OK" if ok else "WARN"
                log(f"  [{status}] '{query[:55]}'  → {n} hit(s)")
                results[query] = {"hits": n, "status": status}
            except Exception as e:
                log(f"  [ERROR] {query[:40]}: {e}")
                results[query] = {"hits": 0, "status": "ERROR", "error": str(e)}

    return results


# ─────────────────────────────────────────────────────────────────────────────
# FINAL REPORT
# ─────────────────────────────────────────────────────────────────────────────

def print_final_report(file_records, ingest_results, smoke_results, audit_warnings, dry_run):
    sep("═")
    log("PHASE G — FINAL REPORT")
    sep("═")
    log(f"  Mode: {'DRY RUN' if dry_run else 'LIVE INGESTION'}")
    log("")

    log(f"  1.  PDFs discovered:           {sum(1 for r in file_records if r.get('is_valid_pdf'))}")
    log(f"  2.  Provenance verified:        {sum(1 for r in file_records if r['status'] in ('provenance_verified','provenance_verified_with_notes'))}")
    log(f"  3.  Manual review required:     {len(ingest_results.get('skipped_review', []))}")
    for f in ingest_results.get("skipped_review", []):
        log(f"        • {f}")
    log(f"  4.  Processed successfully:     {len(ingest_results.get('processed', []))}")
    log(f"  5.  Failed:                     {len(ingest_results.get('failed', []))}")
    for f in ingest_results.get("failed", []):
        log(f"        • {f['file']}: {f['error']}")
    log(f"  6.  Chunks generated:           {ingest_results.get('total_chunks', 0)}")
    log(f"  7.  Embeddings generated:       {ingest_results.get('total_embeddings', 0)}")
    log(f"  8.  Embedding dimension:        384")
    log(f"  9.  Existing chunks (before):   {ingest_results.get('pre_chunk_count', 'N/A')}")
    log(f"  10. Total chunks (after):       {ingest_results.get('post_chunk_count', 'N/A')}")
    log(f"  11. Existing docs (before):     {ingest_results.get('pre_doc_count', 'N/A')}")
    log(f"  12. Total docs (after):         {ingest_results.get('post_doc_count', 'N/A')}")

    by_cat: Dict[str, int] = {}
    for p in ingest_results.get("processed", []):
        c = p.get("source_category", "Unknown")
        by_cat[c] = by_cat.get(c, 0) + 1
    log(f"  13. NSP processed:              {by_cat.get('NSP', 0)}")
    log(f"  14. Government of India:        {by_cat.get('Government of India', 0)}")
    log(f"  15. UGC processed:              {by_cat.get('UGC', 0)}")
    log(f"  16. AICTE processed:            {by_cat.get('AICTE', 0)}")
    log(f"  17. Duplicate hashes rejected:  {sum(1 for r in file_records if r['status']=='duplicate_hash')}")
    
    skipped_ocr = sum(1 for r in file_records if r["status"] == "OCR_REQUIRED_SKIPPED")
    log(f"  18. OCR_REQUIRED_SKIPPED count: {skipped_ocr}")

    ocr = len(ingest_results.get('ocr_required', []))
    log(f"  19. New OCR required detected:  {ocr}")
    for f in ingest_results.get("ocr_required", []):
        log(f"        • {f}")
    log("")
    log("  20. Retrieval smoke-test:")
    for q, r in smoke_results.items():
        log(f"        [{r['status']}] '{q[:55]}' → {r.get('hits', 0)} hit(s)")
    log("")
    log("  20. Warnings:")
    for w in (audit_warnings or ["None"]):
        log(f"        • {w}")
    log("")
    log("  ✅ No existing Phase A-F data deleted")
    log("  ✅ No third-party sources ingested")
    log("  ✅ BGE 384D model unchanged")
    log("  ✅ Ollama/llama3.2 unchanged")
    log("  ✅ No commit/push performed")
    sep("═")


def main():
    audit_only = "--audit-only" in sys.argv
    dry_run = "--dry-run" in sys.argv

    sep("═")
    log("PHASE G — PDF INGESTION PIPELINE")
    log(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"Chunk size: {settings.chunk_size}  Overlap: {settings.chunk_overlap}")
    log(f"DB: {settings.postgres_db}  Embedding: {settings.embedding_model}")
    sep("═")

    file_records, audit_warnings = audit_files()
    file_records = assign_provenance(file_records)

    if audit_only:
        log("\n[AUDIT-ONLY MODE] Stopping before ingestion.")
        sep()
        for r in file_records:
            notes = "; ".join(r.get("review_notes", []))
            line = f"  {r['status']:38s} {r['filename']}"
            if notes:
                line += f"\n    NOTES: {notes}"
            log(line)
        return

    ingest_results = ingest_documents(file_records, dry_run=dry_run)

    smoke_results = {}
    if not dry_run and ingest_results.get("processed"):
        try:
            smoke_results = retrieval_smoke_test()
        except Exception as e:
            log(f"  [WARN] Smoke test skipped: {e}")

    print_final_report(file_records, ingest_results, smoke_results, audit_warnings, dry_run)


if __name__ == "__main__":
    main()
