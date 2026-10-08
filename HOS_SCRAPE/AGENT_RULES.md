# AGENT RULES: House of Sport jobs + mall-loan scrape (HOS_SCRAPE)
Repo root: /home/user/dks-research (ignore C:\Users\... paths in CLAUDE.md; same folder). Read this whole file first.

## Mission
The user (buy-side analyst, long DKS) wants MORE store-level evidence on DICK'S **House of Sport (HoS)** sales productivity (sales gain per relocated/new HoS store vs the Street's ~$20M increment), from two evidence types:
1. **Jobs data** for HoS openings (headcount ⇒ sales via $/job). The BLS QCEW county event study is ALREADY DONE (34 of 36 HoS events usable, data only through 2026Q1; year-1 ≈ +110 net jobs × ~$215K/job ≈ $21-24M; Johnson City calibration ≈ $70K/job). Your job is OTHER job sources and HoS events/stores the 34 miss or measure poorly (esp. openings Q4 2025 → today, and pipeline stores).
2. **Mall-loan (CMBS) filings** that disclose DICK'S HoS store sales. ALREADY FOUND: Tampa HoS ($12.3M first 3 months), Empire Mall / Washington Square (landlord underwriting $35M; $22.8M / $16.4M gains), Ridgedale Center Minnetonka ($31,197,485 TTM 12/2024, $271/sf); the CMBS panel holds 22 DICK'S boxes from 517 cached docs (EDGAR full-text search, forms FWP/424B2/424H/424B5/424B3, 2019-2026).
Separately: any **Foot Locker / Champs / Kids Foot Locker store sales** in the same filings go in a separate "FL" section (useful if it shows FL recovering: 2025-2026 sales vs earlier years).
HoS ONLY for the jobs and DKS mall-loan parts (not Field House, not Golf Galaxy).

## Already-known material (novelty check — the user does NOT want data we already have)
Before recording a finding, Grep its key number/store/term across: `THESIS_SCRAPE/` (esp. wave1/H02, H03, H04, H06, H07; wave2/B1-B9; wave3; KNOWN_BRIEF.md), `EVIDENCE_BOOK/` (esp. S2.md, S3.md), `CORE_NOTES/00_CORE_DIGEST.md`, and `HOS_SCRAPE/wave*/`. Raw CSVs from the earlier run may be under `THESIS_SCRAPE/raw/` (B5_event_summary.csv = the 34-36 QCEW events; B8_cmbs_store_panel.csv; B9_*.csv; H04_*.csv; H07_*.csv) — use them to avoid duplicates.
Tag each item NEW (not in folder) or KNOWN (skip; one line max).

## Evidence standard
- Hard numbers with date, store, city/county, source URL (or script + data path), and method. Grade: **A** hard and quantified (headcount, sales, $ underwriting) for a specific HoS; **B** quantified but indirect / planned (e.g. "hiring 150"), or credible named source; **C** anecdotal. **X** = evidence against (lower sales/jobs than modeled, closures, weak stores). Always report X.
- For each jobs data point give the implied sales at both $215K/job and $70K/job (label INFERENCE).
- Cite your methodology clearly (the user asked): source, query/filters, dates, sample, any adjustment.

## Tools, cost discipline
- HARD BUDGET: about 40 tool calls. Do heavy work in Python scripts that print compact tables only; never dump raw pages into your context. Stop an avenue once it stops producing new information.
- WebSearch and WebFetch work; Bash has full internet (`requests`, `curl_cffi` impersonate="chrome", `bs4`, `lxml`, `pandas`, `pypdf` if installed — `pip install -q pypdf` if needed). Run Python with `python3 -I` when it reads downloaded files.
- SEC EDGAR full-text search: `https://efts.sec.gov/LATEST/search-index?q="..."&forms=...&dateRange=custom&startdt=...&enddt=...` (send a User-Agent like "Research palazzolojustin@gmail.com"; ≤5 req/s; the `forms` filter has dropped docs before — also try without it). Documents: `https://www.sec.gov/Archives/edgar/data/...`.
- Wayback: `http://web.archive.org/cdx/search/cdx?url=...&output=json` then `http://web.archive.org/web/<ts>id_/<url>`. BLS QCEW open data: `https://data.bls.gov/cew/data/api/<year>/<q>/area/<fips>.csv`.
- Be polite; no logins, no paid services, no contacting people, no form submissions, no API keys scraped from pages.
- Save raw files to `HOS_SCRAPE/raw/<ID>/` (git-ignored), scripts to `HOS_SCRAPE/scripts/<ID>_*.py`, tidy datasets to `HOS_SCRAPE/data/<ID>_*.csv`. Do not edit other folders. Do not run git.

## Output
Write `HOS_SCRAPE/wave<N>/<ID>.md` early and append as you go (if it exists, it is your own partial work: continue it). Structure:
```
# <ID>: <avenue>
## Methodology (source, queries, filters, dates, sample, adjustments; scripts/data paths)
## NEW findings (strongest first): - [A|B|C] store | metric with number | date | source | implied sales $215K / $70K if jobs
## FL section (Foot Locker / Champs store sales, if any)
## Evidence AGAINST (X)
## Already known (one line each)
## Leads for next wave
## Avenue verdict: PRODUCTIVE / THIN / DEAD (one line why)
STATUS: COMPLETE
```
Final reply to the orchestrator: ≤8 lines (counts of NEW A/B/C/X, top 3 with numbers, verdict, best lead).
