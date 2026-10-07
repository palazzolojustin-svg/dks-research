# AGENT RULES: Foot Locker inventory-shift overnight scrape (FL_INVENTORY_SCRAPE)
Read this whole file before doing anything. Repo root: /home/user/dks-research (ignore the C:\Users\... paths in CLAUDE.md; they refer to the same folder on the user's PC).

## Mission
The user (buy-side analyst, long DKS) wants NOVEL, HARD evidence for one thesis:
**Foot Locker (FL, owned by DICK'S since 2025-09-08) is shifting its underlying inventory/SKU mix (Fast Break resets, ~30% SKU cut, apparel re-added, new brands such as Salomon, first fully DKS-bought assortment from back-to-school 2026, less dependence on legacy Nike lifestyle/retro silhouettes), and the new inventory will get significantly higher consumer uptake (sell-through, traffic, conversion, comps) and need significantly less discounting (markdowns, % of assortment on sale, discount depth). Consensus does not reflect this, or reflects it too late.**
Scope = the Foot Locker Business only: Foot Locker, Kids Foot Locker, Champs, WSS, atmos, FL Europe/APAC, plus brands only insofar as they affect FL inventory. NOT core DICK'S stores.
Today is 2026-10-07. DKS FY2026 = year ending 2027-01-30. Q3 FY26 = Aug-Oct 2026 (reported ~Nov 24-25, 2026); Q4 FY26 = Nov 2026-Jan 2027. FL enters the comp base in Q4 FY26.

Consensus we measure against (Bloomberg, pulled 2026-10-04): FL PF comp 3Q26E +0.34%, 4Q26E +0.97%, 1Q27E +1.20%, 2Q27E +1.92%, then 2.75% → 3.53%; FL revenue 3Q26E $1,738.14M, 4Q26E $2,139.45M, 1Q27E $1,749.00M, 2Q27E $1,725.35M; FY26E $7,401.59M, FY27E $7,366.80M; FL OI 3Q26E −$71.34M (−4.11%), 4Q26E +$14.00M (0.37%), 1Q27E $18.22M, 2Q27E −$13.26M; FY26E −$72.61M, FY27E +$19.71M (0.23%), FY28E $108.64M; FL GM FY26E ~25.9%, FY27E ~26.8-27.0%, FY28E ~27.5% (corrected by F02: BBG row is shifted one year); 1Q27E FL GM ~27.87% ≈ flat y/y. Use only QUARTERLY FL comp consensus (BBG annual FL comp row is unreliable). Company FY26 FL guide (8/25/26): PF comp −2% to 0%, sales $7.4-7.5B, segment profit −$80M to −$40M. Actual FL: Q1 FY26 comp +0.6%, GM 27.90%; Q2 FY26 comp −3.6%, GM 25.66%.

## The novelty rule (MOST IMPORTANT: the user explicitly does NOT want data we already have)
Before recording any finding, Grep its key number/term/claim across the whole folder:
`CORE_NOTES/`, `WORKING_NOTES/`, `EVIDENCE_BOOK/`, `THESIS_SCRAPE/`, `PB_SCRAPE/`, `FL_EUROPE_SCRAPE/` (incl. `baseline/primers/`), and `FL_INVENTORY_SCRAPE/wave*/` (other agents' output).
Already-known facts include (non-exhaustive): Fast Break ~30% SKU cut, wall reset, apparel re-added; 11 → 21 → ~100 → ~250 → "north of 300, 350" doors; double-digit / >6% Fast Break comps; Salomon added 7/18; "Colors"/"It Will Always Be Foot Locker" campaign; Stripers payroll; FL inventory "cleanest ever"; FL inv $1.8B/$1.5B/$1.7B/$2.0B; UBS Fast Break comp contribution 60 → 120 → ~210bps; E12/E14 expert quotes; Nike share of FL purchases 59%; JPM/Barclays promo trackers. Do not report these as findings.
Tag every finding:
- `NEW` = not in the folder at all (web-sourced, or computed fresh by you from data you collected).
- `KNOWN` = already in the folder → do NOT list as a finding; at most one line in an "Already known" section.
Only NEW findings count. A new number that updates a known fact (e.g. a fresh store count, a newer date) is NEW if the specific number/date is not in the folder.

## Evidence standard
- Hard data > opinions. Best: numbers you collected/computed yourself (catalog counts, % on sale, price/discount distributions, review counts, traffic, search trends, import records, store census) with dates and a time series or a before/after or Fast-Break-vs-legacy comparison.
- Every finding needs: the number, unit, period/date, source URL (or script + raw file path), and how you got it.
- Grade each NEW finding: **A** = hard, quantified, directly supports higher uptake or less discounting for the NEW FL inventory, and is verifiable; **B** = quantified but indirect, or strong qualitative from a credible primary source (company exec, brand exec, filing, named trade press); **C** = anecdotal/soft (single social post, unnamed claim). Also log **X** = evidence AGAINST the thesis (always report these; the user needs them).
- Say for each finding what it implies for consensus: which line (FL comp, FL GM, FL OI, FL revenue), which quarter, and direction/size if you can estimate it (label estimates as INFERENCE).

## Tools and methods
- WebSearch works. WebFetch works for most sites. Bash has full internet: use `curl` or Python (`requests`, `curl_cffi` with `impersonate="chrome"` for bot-protected sites, `bs4`, `lxml`, `pandas`, `pytrends`, `playwright` with Chromium at /opt/pw-browsers if needed). Run Python with `python3 -I` when it reads downloaded files.
- reddit.com and stockx.com return 403 to plain curl: try `curl_cffi` impersonation, `old.reddit.com/.../.json`, `api.pullpush.io`, `arctic-shift.photon-reddit.com/api`, or search engines.
- Wayback Machine: `http://web.archive.org/cdx/search/cdx?url=...&output=json&from=2024&to=2026` then `http://web.archive.org/web/<timestamp>id_/<url>`.
- Be polite: small delays between requests, no logins, no paid services, no contacting people, no form submissions.
- Save raw downloads to `FL_INVENTORY_SCRAPE/raw/<YOUR_ID>/` (git-ignored), scripts to `FL_INVENTORY_SCRAPE/scripts/<YOUR_ID>_*.py`, and any tidy dataset you build (CSV, small) to `FL_INVENTORY_SCRAPE/data/<YOUR_ID>_*.csv`.
- Do NOT edit anything in SOURCE/, CORE_NOTES/, WORKING_NOTES/ or the other scrape folders. Do NOT run git.

## Output file (crash-safe)
Write to `FL_INVENTORY_SCRAPE/wave<N>/<YOUR_ID>.md`. Create it early and append as you go (if the file already exists, it is your own partial work from a crashed run: keep it and continue). Structure:
```
# <ID>: <avenue>
## Method (what you scraped, how, dates, row counts; scripts/data paths)
## NEW findings (ranked, strongest first)
- [A|B|C] <one-sentence finding with the number> | period | source/URL or script+data | consensus implication
## Evidence AGAINST (X)
## Already known (one line each, file › section)
## Leads for next wave (specific URLs/endpoints/ideas that looked promising but you ran out of time for)
## Avenue verdict: PRODUCTIVE / THIN / DEAD, and why (one line)
STATUS: COMPLETE
```
Your final reply to the orchestrator: 5-10 lines: count of NEW A/B/C/X findings, the top 3 with numbers, the avenue verdict, and the best lead.
Work for as long as it is productive (it is fine to run for hours). Stop an avenue when it stops producing new information, not before.
