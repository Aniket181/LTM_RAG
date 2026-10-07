# Phase G — Corrected PDF Collection Plan
**Date:** 2026-10-07
**Status:** CANDIDATE PLAN — NOT YET VERIFIED. No PDFs downloaded.

---

> [!IMPORTANT]
> This document is a **candidate plan** only. No entries are "verified" unless you have personally opened the official source page, confirmed the PDF exists, and downloaded it from an approved official domain.
>
> **Do NOT count any entry toward the 50-document target until it is physically downloaded, hash-checked, and provenance-recorded.**

---

## Source Restriction Policy

Only these four source categories are permitted — **not simply any .gov.in domain**:

| Category | Approved Domains | Examples |
| :--- | :--- | :--- |
| **NSP** | scholarships.gov.in | Centrally-sponsored scheme guidelines hosted on NSP |
| **Government of India** | socialjustice.gov.in, tribal.gov.in, minorityaffairs.gov.in, education.gov.in, dohe-education.gov.in | Central ministry/department PDFs |
| **UGC** | ugc.gov.in, ugc.ac.in | Fellowship/scholarship guidelines from UGC |
| **AICTE** | aicte-india.org, aicte.gov.in | Student scheme guidelines from AICTE |

**Prohibited — even if domain is .gov.in:**
- State government portals (e.g., scholarship.up.gov.in, oasis.gov.in)
- University/institution websites
- myScheme.gov.in (aggregator portal — not a primary source)
- NIC portals hosting copies of state schemes
- Any third-party mirror or copy

---

## URL Verification Status Definitions

| Status | Meaning |
| :--- | :--- |
| `MANUAL_DISCOVERY_REQUIRED` | Official source page is known but direct PDF URL has not been confirmed |
| `SOURCE_PAGE_CONFIRMED` | Official source page was accessed and confirmed to host the scheme |
| `PDF_URL_VERIFIED` | The actual direct PDF URL was opened and confirmed |
| `REQUIRES_MANUAL_VERIFICATION` | Scheme existence or official PDF availability is uncertain |
| `DOWNLOADED` | PDF has been downloaded, hash-checked, and placed in correct directory |

---

## Candidate Collection Table

### AICTE — Target: 8–12 PDFs
**Official Entry Point:** https://www.aicte-india.org/schemes/students-development-schemes

*Note: The AICTE schemes page was confirmed accessible (HTTP 200). Individual scheme sub-pages (e.g., /Pragati, /Saksham) returned 404. Direct PDF URLs are NOT fabricated — all require manual discovery from the schemes list.*

| ID | Opportunity | Source Organization | Official Source Page | Direct PDF URL | Academic Year | Unique Opportunity? | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| A01 | Pragati Scholarship Scheme (Girl Students in Technical Education) | All India Council for Technical Education | https://www.aicte-india.org/schemes/students-development-schemes | MANUAL_DISCOVERY_REQUIRED | 2024-25 | Yes | REQUIRES_MANUAL_VERIFICATION |
| A02 | Saksham Scholarship Scheme (Students with Disabilities in Technical Education) | All India Council for Technical Education | https://www.aicte-india.org/schemes/students-development-schemes | MANUAL_DISCOVERY_REQUIRED | 2024-25 | Yes | REQUIRES_MANUAL_VERIFICATION |
| A03 | AICTE-NEC Scholarship (North East Council — Technical Education) | All India Council for Technical Education | https://www.aicte-india.org/schemes/students-development-schemes | MANUAL_DISCOVERY_REQUIRED | 2024-25 | Yes | REQUIRES_MANUAL_VERIFICATION |
| A04 | AICTE National Doctoral Fellowship | All India Council for Technical Education | https://www.aicte-india.org/bureaus/scholarships-and-grants | MANUAL_DISCOVERY_REQUIRED | 2024-25 | Yes | REQUIRES_MANUAL_VERIFICATION |
| A05 | AICTE Tuition Fee Waiver Scheme | All India Council for Technical Education | https://www.aicte-india.org/schemes/students-development-schemes | MANUAL_DISCOVERY_REQUIRED | 2024-25 | Yes | REQUIRES_MANUAL_VERIFICATION |
| A06 | AICTE Research Promotion Scheme | All India Council for Technical Education | https://www.aicte-india.org/bureaus/scholarships-and-grants | MANUAL_DISCOVERY_REQUIRED | 2024-25 | Yes | REQUIRES_MANUAL_VERIFICATION |
| A07 | AICTE Margdarshan Scheme (Mentoring of Technical Institutions) | All India Council for Technical Education | https://www.aicte-india.org/schemes/institutional-development-schemes | MANUAL_DISCOVERY_REQUIRED | 2024-25 | No — Institutional, not student | REQUIRES_MANUAL_VERIFICATION |
| A08 | ATAL (Accelerated Technology Assessment and Licensing) Fellowship | All India Council for Technical Education | https://www.aicte-india.org/schemes/students-development-schemes | MANUAL_DISCOVERY_REQUIRED | 2024-25 | Yes | REQUIRES_MANUAL_VERIFICATION |

**AICTE Candidate Count:** 8 (7 student-relevant)
**AICTE Verified PDF URLs:** 0
**AICTE Requiring Manual Discovery:** 8

---

### NSP — Target: 10–15 PDFs
**Official Entry Point:** https://scholarships.gov.in/public/schemeGuidelines/centralsOrsponsoredOrstate

*Note: The NSP scheme guidelines page was confirmed accessible (HTTP 200). It renders via JavaScript — PDF links were not extractable without a browser. All direct PDF URLs require manual discovery by opening the page in a browser and clicking each scheme's guideline link.*

*Duplicate Alert: Several NSP-listed schemes are administered by MoE, MoSJE, MoTA, and MoMA. If the source PDF is hosted on the ministry's domain (not scholarships.gov.in), count it under "Government of India" — not "NSP". Do not count the same PDF twice.*

| ID | Opportunity | Source Organization | Official Source Page | Direct PDF URL | Academic Year | Unique Opportunity? | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| N01 | Central Sector Scheme of Scholarships for College and University Students (CSSS) | Ministry of Education | https://scholarships.gov.in/public/schemeGuidelines/centralsOrsponsoredOrstate | MANUAL_DISCOVERY_REQUIRED | 2024-25 | Yes | REQUIRES_MANUAL_VERIFICATION |
| N02 | National Means-cum-Merit Scholarship (NMMS) | Ministry of Education | https://scholarships.gov.in/public/schemeGuidelines/centralsOrsponsoredOrstate | MANUAL_DISCOVERY_REQUIRED | 2024-25 | Yes | REQUIRES_MANUAL_VERIFICATION |
| N03 | Post-Matric Scholarship for Scheduled Castes (SC) | Ministry of Social Justice & Empowerment | https://scholarships.gov.in/public/schemeGuidelines/centralsOrsponsoredOrstate | MANUAL_DISCOVERY_REQUIRED | 2024-25 | Yes — *Possible duplicate with GOI list* | REQUIRES_MANUAL_VERIFICATION |
| N04 | Post-Matric Scholarship for Scheduled Tribes (ST) | Ministry of Tribal Affairs | https://scholarships.gov.in/public/schemeGuidelines/centralsOrsponsoredOrstate | MANUAL_DISCOVERY_REQUIRED | 2024-25 | Yes — *Possible duplicate with GOI list* | REQUIRES_MANUAL_VERIFICATION |
| N05 | Post-Matric Scholarship for OBC Students | Ministry of Social Justice & Empowerment | https://scholarships.gov.in/public/schemeGuidelines/centralsOrsponsoredOrstate | MANUAL_DISCOVERY_REQUIRED | 2024-25 | Yes — *Possible duplicate with GOI list* | REQUIRES_MANUAL_VERIFICATION |
| N06 | Post-Matric Scholarship for EBC (Economically Backward Classes) | Ministry of Social Justice & Empowerment | https://scholarships.gov.in/public/schemeGuidelines/centralsOrsponsoredOrstate | MANUAL_DISCOVERY_REQUIRED | 2024-25 | Yes | REQUIRES_MANUAL_VERIFICATION |
| N07 | Pre-Matric Scholarship for Minority Students | Ministry of Minority Affairs | https://scholarships.gov.in/public/schemeGuidelines/centralsOrsponsoredOrstate | MANUAL_DISCOVERY_REQUIRED | 2024-25 | Yes — *Possible duplicate with GOI list* | REQUIRES_MANUAL_VERIFICATION |
| N08 | Post-Matric Scholarship for Minority Students | Ministry of Minority Affairs | https://scholarships.gov.in/public/schemeGuidelines/centralsOrsponsoredOrstate | MANUAL_DISCOVERY_REQUIRED | 2024-25 | Yes — *Possible duplicate with GOI list* | REQUIRES_MANUAL_VERIFICATION |
| N09 | Merit-cum-Means Scholarship for Professional and Technical Courses (Minorities) | Ministry of Minority Affairs | https://scholarships.gov.in/public/schemeGuidelines/centralsOrsponsoredOrstate | MANUAL_DISCOVERY_REQUIRED | 2024-25 | Yes — *Possible duplicate with GOI list* | REQUIRES_MANUAL_VERIFICATION |
| N10 | Scholarship for Top Class Education for SC Students | Ministry of Social Justice & Empowerment | https://scholarships.gov.in/public/schemeGuidelines/centralsOrsponsoredOrstate | MANUAL_DISCOVERY_REQUIRED | 2024-25 | Yes — *Possible duplicate with GOI list* | REQUIRES_MANUAL_VERIFICATION |
| N11 | Post-Matric Scholarship for DNT/SNT/NT Communities | Ministry of Social Justice & Empowerment | https://scholarships.gov.in/public/schemeGuidelines/centralsOrsponsoredOrstate | MANUAL_DISCOVERY_REQUIRED | 2024-25 | Yes | REQUIRES_MANUAL_VERIFICATION |
| N12 | Ishan Uday Special Scholarship Scheme for North Eastern Region | UGC | https://scholarships.gov.in/public/schemeGuidelines/centralsOrsponsoredOrstate | MANUAL_DISCOVERY_REQUIRED | 2024-25 | Yes — *Possible duplicate with UGC list; assign to UGC if PDF on ugc.gov.in* | REQUIRES_MANUAL_VERIFICATION |
| N13 | National Fellowship for OBC Students | Ministry of Social Justice & Empowerment | https://scholarships.gov.in/public/schemeGuidelines/centralsOrsponsoredOrstate | MANUAL_DISCOVERY_REQUIRED | 2024-25 | Yes | REQUIRES_MANUAL_VERIFICATION |

**NSP Candidate Count:** 13
**NSP Verified PDF URLs:** 0
**NSP Requiring Manual Discovery:** 13

> [!WARNING]
> N03–N10, N12 may also appear in the Government of India list. When you download the PDF, check the domain it's served from. If it's on socialjustice.gov.in, tribal.gov.in, etc., assign it to "Government of India" and do NOT count it under NSP.

---

### Government of India Ministries — Target: 15–20 PDFs

*Note: Only central government ministry/department portals are accepted. State government URLs (e.g., oasis.gov.in for West Bengal OBC scholarships) are NOT permitted.*

**Ministry of Social Justice & Empowerment:** https://socialjustice.gov.in/

| ID | Opportunity | Source Organization | Official Source Page | Direct PDF URL | Academic Year | Unique Opportunity? | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| G01 | Post-Matric Scholarship for SC Students — Guidelines | Ministry of Social Justice & Empowerment | https://socialjustice.gov.in/index.php/schemes | MANUAL_DISCOVERY_REQUIRED | 2024-25 | Yes — may overlap with N03 | REQUIRES_MANUAL_VERIFICATION |
| G02 | Top Class Education Scholarship for SC Students — Guidelines | Ministry of Social Justice & Empowerment | https://socialjustice.gov.in/index.php/schemes | MANUAL_DISCOVERY_REQUIRED | 2024-25 | Yes — may overlap with N10 | REQUIRES_MANUAL_VERIFICATION |
| G03 | National Fellowship for SC Students | Ministry of Social Justice & Empowerment | https://socialjustice.gov.in/index.php/schemes | MANUAL_DISCOVERY_REQUIRED | 2024-25 | Yes | REQUIRES_MANUAL_VERIFICATION |
| G04 | National Fellowship for OBC Students | Ministry of Social Justice & Empowerment | https://socialjustice.gov.in/index.php/schemes | MANUAL_DISCOVERY_REQUIRED | 2024-25 | Yes — may overlap with N13 | REQUIRES_MANUAL_VERIFICATION |
| G05 | Scholarship for Students with Disabilities (Post-Matric) | Ministry of Social Justice & Empowerment | https://socialjustice.gov.in/index.php/schemes | MANUAL_DISCOVERY_REQUIRED | 2024-25 | Yes | REQUIRES_MANUAL_VERIFICATION |

**Ministry of Tribal Affairs:** https://tribal.gov.in/

| ID | Opportunity | Source Organization | Official Source Page | Direct PDF URL | Academic Year | Unique Opportunity? | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| G06 | Post-Matric Scholarship for ST Students — Guidelines | Ministry of Tribal Affairs | https://tribal.gov.in/ | MANUAL_DISCOVERY_REQUIRED | 2024-25 | Yes — may overlap with N04 | REQUIRES_MANUAL_VERIFICATION |
| G07 | National Fellowship for ST Students | Ministry of Tribal Affairs | https://tribal.gov.in/ | MANUAL_DISCOVERY_REQUIRED | 2024-25 | Yes | REQUIRES_MANUAL_VERIFICATION |
| G08 | National Overseas Scholarship for ST Students | Ministry of Tribal Affairs | https://tribal.gov.in/ | MANUAL_DISCOVERY_REQUIRED | 2024-25 | Yes | REQUIRES_MANUAL_VERIFICATION |

**Ministry of Minority Affairs:** https://www.minorityaffairs.gov.in/

| ID | Opportunity | Source Organization | Official Source Page | Direct PDF URL | Academic Year | Unique Opportunity? | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| G09 | Pre-Matric Scholarship for Minorities — Official Guidelines | Ministry of Minority Affairs | https://www.minorityaffairs.gov.in/ | MANUAL_DISCOVERY_REQUIRED | 2024-25 | Yes — may overlap with N07 | REQUIRES_MANUAL_VERIFICATION |
| G10 | Post-Matric Scholarship for Minorities — Official Guidelines | Ministry of Minority Affairs | https://www.minorityaffairs.gov.in/ | MANUAL_DISCOVERY_REQUIRED | 2024-25 | Yes — may overlap with N08 | REQUIRES_MANUAL_VERIFICATION |
| G11 | Merit-cum-Means Scholarship for Minority Communities | Ministry of Minority Affairs | https://www.minorityaffairs.gov.in/ | MANUAL_DISCOVERY_REQUIRED | 2024-25 | Yes — may overlap with N09 | REQUIRES_MANUAL_VERIFICATION |

**Ministry of Education:** https://www.education.gov.in/ or https://dohe-education.gov.in/

| ID | Opportunity | Source Organization | Official Source Page | Direct PDF URL | Academic Year | Unique Opportunity? | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| G12 | Central Sector Scheme of Scholarships (CSSS) — Official Guidelines | Ministry of Education | https://www.education.gov.in/scholarship-and-fellowships-students | MANUAL_DISCOVERY_REQUIRED | 2024-25 | Yes — may overlap with N01 | REQUIRES_MANUAL_VERIFICATION |
| G13 | National Means-cum-Merit Scholarship Scheme (NMMS) Guidelines | Ministry of Education | https://www.education.gov.in/scholarship-and-fellowships-students | MANUAL_DISCOVERY_REQUIRED | 2024-25 | Yes — may overlap with N02 | REQUIRES_MANUAL_VERIFICATION |
| G14 | PG Scholarship for University Rank Holders (SC/ST) — Guidelines | Ministry of Education | https://www.education.gov.in/scholarship-and-fellowships-students | MANUAL_DISCOVERY_REQUIRED | 2024-25 | Yes | REQUIRES_MANUAL_VERIFICATION |
| G15 | PG Scholarship for Professional Courses (SC/ST) | Ministry of Education | https://www.education.gov.in/scholarship-and-fellowships-students | MANUAL_DISCOVERY_REQUIRED | 2024-25 | Yes | REQUIRES_MANUAL_VERIFICATION |

**GOI Candidate Count:** 15
**GOI Verified PDF URLs:** 0
**GOI Requiring Manual Discovery:** 15

---

### UGC — Target: 8–12 PDFs
**Official Entry Point:** https://www.ugc.gov.in/Home/student_Corner

*Note: UGC student corner was confirmed accessible (HTTP 200). It lists 2 fellowships and 2 scholarships with "View" links. PDF delivery is session-based — direct URL fetching returns the HTML homepage. All PDF links require manual browser navigation.*

| ID | Opportunity | Source Organization | Official Source Page | Direct PDF URL | Academic Year | Unique Opportunity? | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| U01 | UGC Junior Research Fellowship (JRF) in Science, Humanities and Social Sciences | University Grants Commission | https://www.ugc.gov.in/Fellowship/stu_Fellowship1 | MANUAL_DISCOVERY_REQUIRED | 2024-25 | Yes | REQUIRES_MANUAL_VERIFICATION |
| U02 | Savitribai Jyotirao Phule Fellowship for Single Girl Child (PG) | University Grants Commission | https://www.ugc.gov.in/Fellowship/stu_Fellowship3 | MANUAL_DISCOVERY_REQUIRED | 2024-25 | Yes | REQUIRES_MANUAL_VERIFICATION |
| U03 | Ishan Uday Special Scholarship Scheme for North Eastern Region | University Grants Commission | https://www.ugc.gov.in/Scholarships/stu_Scholarship5 | MANUAL_DISCOVERY_REQUIRED | 2024-25 | Yes — *If PDF on ugc.gov.in, assign here; if on scholarships.gov.in, assign to NSP* | REQUIRES_MANUAL_VERIFICATION |
| U04 | National Scholarship for Post Graduate Studies (NPGS) | University Grants Commission | https://www.ugc.gov.in/Scholarships/stu_Scholarship6 | MANUAL_DISCOVERY_REQUIRED | 2024-25 | Yes | REQUIRES_MANUAL_VERIFICATION |
| U05 | PG Indira Gandhi Scholarship for Single Girl Child | University Grants Commission | https://www.ugc.gov.in/Home/student_Corner | MANUAL_DISCOVERY_REQUIRED | 2024-25 | Yes | REQUIRES_MANUAL_VERIFICATION |
| U06 | UGC NET/JRF Official Notification (current cycle) | University Grants Commission | https://www.ugc.gov.in/ | MANUAL_DISCOVERY_REQUIRED | 2024-25 | Yes — Qualifying exam, not a scholarship per se | REQUIRES_MANUAL_VERIFICATION |
| U07 | UGC Research Awards Scheme | University Grants Commission | https://www.ugc.gov.in/Home/student_Corner | MANUAL_DISCOVERY_REQUIRED | 2024-25 | Yes | REQUIRES_MANUAL_VERIFICATION |

**UGC Candidate Count:** 7
**UGC Verified PDF URLs:** 0
**UGC Requiring Manual Discovery:** 7

---

## Summary of Candidate Plan

| Metric | Count |
| :--- | :--- |
| Total candidate documents | 43 |
| NSP candidates | 13 |
| Government of India candidates | 15 |
| UGC candidates | 7 |
| AICTE candidates | 8 |
| Candidates with verified direct PDF URLs | **0** |
| Candidates requiring manual discovery | **43** |
| Unique opportunities (deduplicated) | ~27–30 (many NSP/GOI overlap) |
| Duplicate opportunity risks identified | 10 (marked in table) |
| Candidates requiring manual verification | 43 |
| Entries removed as non-student/irrelevant | 1 (A07 — Institutional scheme) |

---

## Duplicate Opportunity Risks

These pairs describe the same underlying scholarship opportunity. Only **one PDF** should be collected per opportunity (preferably from the ministry's primary domain):

| NSP Entry | GOI Entry | Resolution |
| :--- | :--- | :--- |
| N03 (SC Post-Matric) | G01 (SC Post-Matric) | Download from socialjustice.gov.in; assign to GOI |
| N04 (ST Post-Matric) | G06 (ST Post-Matric) | Download from tribal.gov.in; assign to GOI |
| N07 (Minority Pre-Matric) | G09 (Minority Pre-Matric) | Download from minorityaffairs.gov.in; assign to GOI |
| N08 (Minority Post-Matric) | G10 (Minority Post-Matric) | Download from minorityaffairs.gov.in; assign to GOI |
| N09 (Minority Merit-cum-Means) | G11 (Minority Merit-cum-Means) | Download from minorityaffairs.gov.in; assign to GOI |
| N10 (SC Top Class) | G02 (SC Top Class) | Download from socialjustice.gov.in; assign to GOI |
| N12 (Ishan Uday via NSP) | U03 (Ishan Uday via UGC) | Download from ugc.gov.in; assign to UGC |
| N13 (OBC Fellowship via NSP) | G04 (OBC Fellowship via GOI) | Download from socialjustice.gov.in; assign to GOI |
| N01 (CSSS via NSP) | G12 (CSSS via MoE) | Download from education.gov.in; assign to GOI |
| N02 (NMMS via NSP) | G13 (NMMS via MoE) | Download from education.gov.in; assign to GOI |

After deduplication: NSP-specific count reduces to approximately **3–5** unique NSP PDFs (only those where the guideline is genuinely hosted on scholarships.gov.in and not on a ministry domain).

---

## Manual Download Workflow

For each candidate:
1. Open the **Official Source Page** from the table above in your browser
2. Locate the scheme/scholarship on that page
3. Click the guideline/notification/PDF link
4. **Confirm the URL** in your browser address bar belongs to an approved domain
5. Download the file
6. Rename it using the convention: `<category>_<scheme_short_name>_<year>.pdf`
7. Place in the correct folder:
   - `data/raw/nsp/`
   - `data/raw/government_of_india/`
   - `data/raw/ugc/`
   - `data/raw/aicte/`
8. After downloading each file, note the **exact URL** you downloaded it from — you'll need this for provenance.json

---

## After Download: Run the Audit

```powershell
cd C:\Users\T10007\Desktop\Ltm_projects\RAG
venvrag\Scripts\activate

# Step 1: Generate provenance template
python scripts/build_corpus_catalogue.py --init-provenance

# Step 2: Fill in data/raw/provenance.json for every downloaded PDF

# Step 3: Run the full audit and generate catalogue + manifest
python scripts/build_corpus_catalogue.py
```

---

## Absolute Source Rules (Precise)

✅ **PERMITTED** — must originate from one of these four approved source categories and their associated official domains:

| Category | Permitted Domains |
| :--- | :--- |
| NSP | scholarships.gov.in |
| Government of India | socialjustice.gov.in, tribal.gov.in, minorityaffairs.gov.in, education.gov.in, dohe-education.gov.in, and other **central government ministry** portals |
| UGC | ugc.gov.in, ugc.ac.in |
| AICTE | aicte-india.org, aicte.gov.in |

❌ **PROHIBITED** (not permitted even if domain ends in .gov.in):
- State government scholarship portals (e.g., oasis.gov.in, scholarship.up.gov.in)
- University/college websites
- myScheme.gov.in (aggregator — not a primary source ministry)
- NIC portals hosting state scheme PDFs
- Any private/commercial website
- Scholarship aggregators (buddy4study, vidyasaarathi, scholarship.com, etc.)
- Educational portals
- Wikipedia
- Google Drive / GitHub copies
- Any third-party PDF mirror or rehost
