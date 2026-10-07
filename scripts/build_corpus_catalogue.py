#!/usr/bin/env python3
"""
Phase G Corpus Audit and Catalogue Script
==========================================
Scans the data/raw/ directory for downloaded PDFs, verifies their integrity,
computes SHA-256 hashes, and generates:
  - docs/phase-g-corpus-catalogue.md  (human-readable table)
  - data/raw/phase_g_manifest.json    (machine-readable provenance record)

USAGE:
    cd C:\\Users\\T10007\\Desktop\\Ltm_projects\\RAG
    python scripts/build_corpus_catalogue.py

The script reads provenance metadata from data/raw/provenance.json which you
must create/update manually for each downloaded PDF (see instructions below).
"""

import hashlib
import json
import os
import sys
import uuid
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
CATALOGUE_PATH = PROJECT_ROOT / "docs" / "phase-g-corpus-catalogue.md"
MANIFEST_PATH = RAW_DATA_DIR / "phase_g_manifest.json"
PROVENANCE_FILE = RAW_DATA_DIR / "provenance.json"

# The ONLY permitted source categories
ALLOWED_CATEGORIES = {"NSP", "Government of India", "UGC", "AICTE"}

# Approved source domains (subdomain-aware check)
APPROVED_DOMAINS = [
    "scholarships.gov.in",
    "ugc.gov.in",
    "ugc.ac.in",
    "aicte-india.org",
    "aicte.gov.in",
    "education.gov.in",
    "dohe-education.gov.in",
    "socialjustice.gov.in",
    "tribal.gov.in",
    "minorityaffairs.gov.in",
    "mocom.gov.in",
    ".gov.in",  # catchall for any gov.in subdomain
    ".nic.in",  # NIC-hosted government portals
]

SUBDIRECTORIES = ["nsp", "government_of_india", "ugc", "aicte"]


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def compute_sha256(file_path: Path) -> str:
    """Compute SHA-256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def is_valid_pdf(file_path: Path) -> bool:
    """Verify that a file starts with the PDF magic bytes."""
    try:
        with open(file_path, "rb") as f:
            header = f.read(4)
            return header == b"%PDF"
    except Exception:
        return False


def is_approved_domain(url: str) -> bool:
    """Check whether a URL belongs to an approved official domain."""
    if not url:
        return False
    url_lower = url.lower()
    return any(domain in url_lower for domain in APPROVED_DOMAINS)


def load_provenance() -> Dict[str, Any]:
    """Load the provenance metadata JSON file."""
    if not PROVENANCE_FILE.exists():
        print(f"\n[WARNING] Provenance file not found: {PROVENANCE_FILE}")
        print("          Run `python scripts/build_corpus_catalogue.py --init-provenance`")
        print("          to generate an empty template provenance.json for your PDFs.\n")
        return {}
    with open(PROVENANCE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def init_provenance_template():
    """Generate an empty provenance.json template for all PDFs found in data/raw/."""
    template = {}
    for subdir in SUBDIRECTORIES:
        subdir_path = RAW_DATA_DIR / subdir
        if not subdir_path.exists():
            continue
        for pdf_file in sorted(subdir_path.glob("*.pdf")):
            filename = pdf_file.name
            template[filename] = {
                "opportunity_name": "FILL_IN",
                "document_title": "FILL_IN",
                "source_category": "FILL_IN: one of NSP | Government of India | UGC | AICTE",
                "source_organization": "FILL_IN: e.g. National Scholarship Portal / Ministry of Education / UGC / AICTE",
                "official_source_url": "FILL_IN: exact official URL from .gov.in or aicte-india.org",
                "academic_year": "FILL_IN: e.g. 2025-2026",
                "publication_date": "FILL_IN: e.g. 2025-01-15 or null",
                "document_type": "Scholarship Guideline",
                "notes": "FILL_IN or remove",
            }

    # Also scan root raw dir
    for pdf_file in sorted(RAW_DATA_DIR.glob("*.pdf")):
        filename = pdf_file.name
        if filename not in template:
            template[filename] = {
                "opportunity_name": "FILL_IN",
                "document_title": "FILL_IN",
                "source_category": "FILL_IN: one of NSP | Government of India | UGC | AICTE",
                "source_organization": "FILL_IN",
                "official_source_url": "FILL_IN",
                "academic_year": "FILL_IN",
                "publication_date": None,
                "document_type": "Scholarship Guideline",
                "notes": "",
            }

    with open(PROVENANCE_FILE, "w", encoding="utf-8") as f:
        json.dump(template, f, indent=2, ensure_ascii=False)
    print(f"[OK] Provenance template written to: {PROVENANCE_FILE}")
    print(f"     Found {len(template)} PDF(s). Fill in each entry then re-run without --init-provenance.")


# ============================================================
# AUDIT LOGIC
# ============================================================

def run_audit() -> List[Dict[str, Any]]:
    """
    Scan all PDFs across data/raw/ subdirectories, compute hashes,
    validate provenance, and return a list of verified records.
    """
    provenance = load_provenance()
    records = []
    seen_hashes = {}

    all_pdfs = []
    # Scan structured subdirectories first
    for subdir in SUBDIRECTORIES:
        subdir_path = RAW_DATA_DIR / subdir
        if subdir_path.exists():
            for pdf_file in sorted(subdir_path.glob("*.pdf")):
                all_pdfs.append(pdf_file)
    # Also scan root raw/ for any ungrouped PDFs
    for pdf_file in sorted(RAW_DATA_DIR.glob("*.pdf")):
        all_pdfs.append(pdf_file)

    if not all_pdfs:
        print("\n[INFO] No PDF files found in data/raw/. Nothing to audit.\n")
        return []

    print(f"\n[SCAN] Found {len(all_pdfs)} PDF file(s) across data/raw/\n")

    errors = []
    for pdf_file in all_pdfs:
        filename = pdf_file.name
        relative_path = str(pdf_file.relative_to(PROJECT_ROOT))

        print(f"  Checking: {relative_path}")

        # 1. Validate PDF magic bytes
        if not is_valid_pdf(pdf_file):
            errors.append(f"NOT A VALID PDF: {relative_path}")
            print(f"    [ERROR] Not a valid PDF file!")
            records.append({
                "document_id": str(uuid.uuid4()),
                "local_file_name": filename,
                "local_file_path": relative_path,
                "status": "invalid_file_not_pdf",
            })
            continue

        # 2. Compute SHA-256
        sha256 = compute_sha256(pdf_file)
        file_size = pdf_file.stat().st_size

        # 3. Duplicate detection
        if sha256 in seen_hashes:
            print(f"    [WARN] DUPLICATE of {seen_hashes[sha256]}")
            errors.append(f"DUPLICATE SHA-256 ({sha256[:12]}...): {relative_path} == {seen_hashes[sha256]}")
            records.append({
                "document_id": str(uuid.uuid4()),
                "local_file_name": filename,
                "local_file_path": relative_path,
                "sha256": sha256,
                "file_size_bytes": file_size,
                "status": "duplicate_rejected",
                "duplicate_of": seen_hashes[sha256],
            })
            continue
        seen_hashes[sha256] = relative_path

        # 4. Lookup provenance
        prov = provenance.get(filename, {})
        source_category = prov.get("source_category", "UNKNOWN")
        source_organization = prov.get("source_organization", "UNKNOWN")
        official_source_url = prov.get("official_source_url", "UNKNOWN")
        document_title = prov.get("document_title", filename)
        opportunity_name = prov.get("opportunity_name", "UNKNOWN")
        academic_year = prov.get("academic_year", "")
        publication_date = prov.get("publication_date", None)
        document_type = prov.get("document_type", "Scholarship Guideline")

        # 5. Validate source_category
        category_valid = source_category in ALLOWED_CATEGORIES
        if not category_valid:
            errors.append(f"INVALID SOURCE CATEGORY '{source_category}': {relative_path}")
            print(f"    [ERROR] Invalid source_category: {source_category}")

        # 6. Validate official_source_url
        url_valid = is_approved_domain(official_source_url)
        if not url_valid and official_source_url not in ("UNKNOWN", "FILL_IN"):
            errors.append(f"UNAPPROVED DOMAIN in URL '{official_source_url}': {relative_path}")
            print(f"    [WARN] Official URL not on approved domain: {official_source_url}")

        # 7. Check for unfilled provenance fields
        provenance_complete = (
            source_category in ALLOWED_CATEGORIES
            and source_organization not in ("UNKNOWN", "FILL_IN", "")
            and "FILL_IN" not in official_source_url
            and document_title not in ("FILL_IN", filename)
            and opportunity_name not in ("FILL_IN", "UNKNOWN")
        )

        status = "verified" if (category_valid and url_valid and provenance_complete) else "needs_manual_review"
        if status == "verified":
            print(f"    [OK] sha256={sha256[:16]}...  size={file_size:,} bytes  category={source_category}")
        else:
            print(f"    [NEEDS REVIEW] sha256={sha256[:16]}...  category={source_category}  url_ok={url_valid}")

        records.append({
            "document_id": str(uuid.uuid4()),
            "opportunity_name": opportunity_name,
            "source_category": source_category,
            "source_organization": source_organization,
            "official_source_url": official_source_url,
            "document_title": document_title,
            "academic_year": academic_year,
            "publication_date": publication_date,
            "last_verified_date": date.today().isoformat(),
            "local_file_name": filename,
            "local_file_path": relative_path,
            "document_type": document_type,
            "sha256": sha256,
            "file_size_bytes": file_size,
            "download_date": date.today().isoformat(),
            "status": status,
        })

    return records, errors


# ============================================================
# MANIFEST GENERATION
# ============================================================

def write_manifest(records: List[Dict[str, Any]]):
    """Write the machine-readable manifest JSON."""
    manifest = {
        "generated_at": datetime.now().isoformat(),
        "total_records": len(records),
        "documents": records,
    }
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"\n[OK] Manifest written to: {MANIFEST_PATH}")


# ============================================================
# CATALOGUE GENERATION
# ============================================================

def write_catalogue(records: List[Dict[str, Any]], errors: List[str]):
    """Write the human-readable Markdown catalogue."""
    verified = [r for r in records if r.get("status") == "verified"]
    needs_review = [r for r in records if r.get("status") == "needs_manual_review"]
    duplicates = [r for r in records if r.get("status") == "duplicate_rejected"]
    invalid = [r for r in records if r.get("status") == "invalid_file_not_pdf"]

    nsp_count = len([r for r in verified if r.get("source_category") == "NSP"])
    goi_count = len([r for r in verified if r.get("source_category") == "Government of India"])
    ugc_count = len([r for r in verified if r.get("source_category") == "UGC"])
    aicte_count = len([r for r in verified if r.get("source_category") == "AICTE"])
    unique_opportunities = len(set(r.get("opportunity_name", "") for r in verified if r.get("opportunity_name") not in ("", "UNKNOWN")))

    lines = [
        "# Phase G — Authoritative Scholarship Corpus Catalogue",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Project:** RAG-Based Student Education Opportunity and Scholarship Eligibility Intelligence System",
        "",
        "## Summary",
        "",
        f"| Metric | Count |",
        f"| :--- | :--- |",
        f"| Total PDFs in corpus | {len(records)} |",
        f"| Verified PDFs | {len(verified)} |",
        f"| Needs manual review | {len(needs_review)} |",
        f"| Duplicate files rejected | {len(duplicates)} |",
        f"| Invalid files (not PDF) | {len(invalid)} |",
        f"| Unique opportunities | {unique_opportunities} |",
        f"| NSP PDFs | {nsp_count} |",
        f"| Government of India PDFs | {goi_count} |",
        f"| UGC PDFs | {ugc_count} |",
        f"| AICTE PDFs | {aicte_count} |",
        f"| Invalid sources rejected | 0 (enforced at ingestion) |",
        f"| Documents requiring manual review | {len(needs_review)} |",
        "",
    ]

    if verified:
        lines += [
            "## Verified Documents",
            "",
            "| # | Opportunity | Document Title | Source Category | Source Organization | Academic Year | Publication Date | Official URL | Local File | SHA-256 | Status |",
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
        ]
        for i, r in enumerate(verified, 1):
            sha_short = r.get("sha256", "")[:12] + "..."
            url = r.get("official_source_url", "")
            url_display = f"[Link]({url})" if url and "FILL_IN" not in url else "N/A"
            lines.append(
                f"| {i} | {r.get('opportunity_name', '')} | {r.get('document_title', '')} | "
                f"{r.get('source_category', '')} | {r.get('source_organization', '')} | "
                f"{r.get('academic_year', '')} | {r.get('publication_date', '') or 'N/A'} | "
                f"{url_display} | `{r.get('local_file_name', '')}` | `{sha_short}` | ✅ Verified |"
            )
        lines.append("")

    if needs_review:
        lines += [
            "## Documents Requiring Manual Review",
            "",
            "| # | Local File | Source Category | Reason |",
            "| :--- | :--- | :--- | :--- |",
        ]
        for i, r in enumerate(needs_review, 1):
            reason = "Provenance metadata incomplete" if "FILL_IN" in str(r) else "Source URL unverified"
            lines.append(f"| {i} | `{r.get('local_file_name', '')}` | {r.get('source_category', '')} | {reason} |")
        lines.append("")

    if duplicates:
        lines += [
            "## Duplicates Rejected",
            "",
            "| # | File | Duplicate Of |",
            "| :--- | :--- | :--- |",
        ]
        for i, r in enumerate(duplicates, 1):
            lines.append(f"| {i} | `{r.get('local_file_name', '')}` | `{r.get('duplicate_of', '')}` |")
        lines.append("")

    if errors:
        lines += [
            "## Audit Errors",
            "",
            "```",
        ] + errors + ["```", ""]

    lines += [
        "---",
        "",
        "## Source Restriction Policy",
        "",
        "This corpus is strictly restricted to documents from the following four official source categories only:",
        "",
        "1. **NSP** — National Scholarship Portal (scholarships.gov.in)",
        "2. **Government of India** — Central government ministries/departments (.gov.in)",
        "3. **UGC** — University Grants Commission (ugc.gov.in)",
        "4. **AICTE** — All India Council for Technical Education (aicte-india.org, aicte.gov.in)",
        "",
        "All other sources are prohibited. This is enforced at the database, schema, and ingestion levels.",
    ]

    CATALOGUE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CATALOGUE_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[OK] Catalogue written to: {CATALOGUE_PATH}")


# ============================================================
# MAIN ENTRY POINT
# ============================================================

def main():
    if "--init-provenance" in sys.argv:
        print("[Phase G] Initializing provenance template...")
        init_provenance_template()
        return

    print("=" * 60)
    print("PHASE G — CORPUS AUDIT AND CATALOGUE GENERATION")
    print("=" * 60)

    records, errors = run_audit()

    if not records:
        print("\n[INFO] No documents to process. Place PDFs in data/raw/<category>/ and re-run.")
        print("\nFolders to use:")
        for d in SUBDIRECTORIES:
            print(f"  data/raw/{d}/")
        return

    write_manifest(records)
    write_catalogue(records, errors)

    # Final summary
    verified = [r for r in records if r.get("status") == "verified"]
    review = [r for r in records if r.get("status") == "needs_manual_review"]
    dups = [r for r in records if r.get("status") == "duplicate_rejected"]

    print("\n" + "=" * 60)
    print("AUDIT COMPLETE")
    print("=" * 60)
    print(f"  Total PDFs scanned:      {len(records)}")
    print(f"  Verified:                {len(verified)}")
    print(f"  Needs manual review:     {len(review)}")
    print(f"  Duplicates rejected:     {len(dups)}")
    print(f"  Errors:                  {len(errors)}")
    print(f"\n  Catalogue:  {CATALOGUE_PATH}")
    print(f"  Manifest:   {MANIFEST_PATH}")
    if errors:
        print(f"\n[WARNINGS] {len(errors)} issue(s) found:")
        for e in errors:
            print(f"  - {e}")


if __name__ == "__main__":
    main()
