# DKS RESEARCH WORKSPACE: operating rules (apply to EVERY response)

This folder is a complete research base on **DICK'S Sporting Goods (DKS)** and its peers (NKE, DECK, ONON, ASO, FL, Adidas/Puma), the sector and macro. Every source file (500 files: SEC filings, transcripts, expert calls, broker research, Bloomberg consensus, market/alt data) was read line by line and converted into dense notes written for Claude, not for humans. Data is current to **2026-10-05**.

## Folder map
| Path | What it is |
|---|---|
| `CORE_NOTES/00_CORE_DIGEST.md` | Always-loaded digest of the core notes: key numbers, guidance history, ratings/PTs, debates, quotes, with `→Cxx` pointers to detail |
| `CORE_NOTES/00_CORE_INDEX.md` | Map of every core file → sources covered |
| `CORE_NOTES/C01_SYNTHESIS_A/B.md` | Pre-built DKS synthesis/primer files (10-K facts, alt data, conference highlights, deal/debt, earnings-call quote bank, expert-call insights, Bloomberg actuals & consensus, financial statements, FL merger proxy, PR bridges, primer, SEC index, street ratings/PT history, street note summaries) |
| `CORE_NOTES/C02_EARNINGS_CALLS_A/B.md` | All 7 DKS earnings calls (Q3 FY24 to Q2 FY26), full Q&A |
| `CORE_NOTES/C03_CONFERENCES_EVENTS_A/B.md` | 7 investor conferences, FL acquisition call, 2026 annual meeting |
| `CORE_NOTES/C04_EXPERT_CALLS.md` | 14 AlphaSense expert calls (Jun-Jul 2026) |
| `CORE_NOTES/C05_CONSENSUS_MARKETDATA_ALTDATA_SLIDES_LETTERS.md` | DKS Bloomberg consensus/estimates, market data, alt data, options/holders/insiders, investor slides, shareholder letters |
| `CORE_NOTES/C06_STREET_RESEARCH_R1..R6.md` | All 45 DKS broker/research notes, chronological (R1 = Aug-Dec 2025 … R6 = Aug-Oct 2026) |
| `CORE_NOTES/data/*.csv` | Raw market-data CSVs (DKS daily OHLCV, options, holders, insiders, ratings, peer closes, peer valuation): load with python for any calculation |
| `WORKING_NOTES/00_WORKING_INDEX.md` | Map of every working-notes file → sources covered |
| `WORKING_NOTES/W01-W09_*.md` | DKS SEC filings: 10-Ks FY22-FY25, 10-Qs FY22Q3-FY26Q2, all 8-Ks + earnings press releases, debt/registration docs, Foot Locker merger prospectus, 425 deal communications, annual reports |
| `WORKING_NOTES/P_*.md` | Peers: NKE/DECK/ONON research, Adidas/Puma/ASO/FL research, NKE/ASO/FL 10-Ks, 10-Qs and FL 8-Ks |
| `WORKING_NOTES/W20_SECTOR_MACRO.md`, `W21_PEER_CONSENSUS_FINANCIALS_AND_PEER_MARKET_DATA.md` | Sector/macro/credit research; Bloomberg consensus for DECK/NKE/ONON + peer market data |
| `SOURCE/` | The original 500 source files, untouched: the ground truth for verification |
| `_MANIFEST/COVERAGE_REPORT.md` | Proof of coverage: every source file → agent, read mode, last line read, notes section |
| `_PREP/` | Build artifacts (deltas, specs, scripts); ignore unless auditing |

Sizes: digest ≈115K chars (~33K tokens); CORE_NOTES 14 files ≈1.79M chars (~510K tokens); WORKING_NOTES 40 files ≈3.46M chars (~990K tokens); vs ~33MB (~8M tokens) of raw source. The core notes are too large to hold in one context, which is why the digest is read directly and the full core notes are read by the K1-K6 agents on every question.
Coverage: `_MANIFEST/COVERAGE_REPORT.md` shows all 500 source files assigned, and every one read to its last line (near-duplicate filings were read as machine-computed deltas against their reference document; see `_PREP/deltas`).

## Notation used in the notes
`[d]` = arithmetic added by the note-writer · `[r]` = table rebuilt from garbled PDF text (verify in SOURCE if a number is critical) · `=same as X` = verbatim duplicate of X, only differences recorded · `[sic]` / `[as written]` = source error kept as printed · `DKS-READ:` = read-through to DKS in peer/sector material · `→C02B` = pointer to the core file holding full detail · `## SRC <path>` = section for one source file (path relative to `SOURCE/`).
Fiscal calendars: **DKS FY ends late Jan/early Feb (FY2025 = year ended 2026-01-31; FY2026 = year ending 2027-01-30 = Bloomberg "2027 Y")**. NKE FY ends May 31; DECK FY ends Mar 31; ONON reports calendar year in CHF; ASO FY ends ~Jan 31; FL FY ended ~Jan 31 (acquired by DKS 2025-09-08).

## MANDATORY PROTOCOL: run for every user question
Default mode is **FULL SWEEP**, every time, unless the user's message starts with `quick:`.

**Step 1: Core digest first.** If the full text of `CORE_NOTES/00_CORE_DIGEST.md` is not already visible in your context (new session, or the context was compacted/summarized), read it in full now before anything else. Use it to frame the question and decide which working notes matter.

**Step 2: Launch ALL sweep agents in ONE message (parallel, `subagent_type: general-purpose`, `run_in_background: false`).**
A. *Core sweep: always all 6 agents, every question.* Each reads its files IN FULL (sequential Read chunks, line 1 to last line) and extracts everything relevant:
  - K1: `CORE_NOTES/C01_SYNTHESIS_A.md`
  - K2: `CORE_NOTES/C01_SYNTHESIS_B.md`
  - K3: `CORE_NOTES/C02_EARNINGS_CALLS_A.md`, `C02_EARNINGS_CALLS_B.md`, `C03_CONFERENCES_EVENTS_A.md`, `C03_CONFERENCES_EVENTS_B.md`
  - K4: `CORE_NOTES/C04_EXPERT_CALLS.md`, `C05_CONSENSUS_MARKETDATA_ALTDATA_SLIDES_LETTERS.md`
  - K5: `CORE_NOTES/C06_STREET_RESEARCH_R1.md`, `R2.md`, `R3.md`
  - K6: `CORE_NOTES/C06_STREET_RESEARCH_R4.md`, `R5.md`, `R6.md`
B. *Working-notes sweep: 2 to 12 agents, chosen from `WORKING_NOTES/00_WORKING_INDEX.md`.* Cover every working-notes file plausibly relevant to the question; for broad questions (thesis, valuation, "everything about X") cover ALL working-notes files. Give each agent ≤ ~300K characters of files to read in full. Peer files are needed for peer, competitive, wholesale, brand-supply, Nike/Hoka/On, Foot Locker or industry questions.
C. If the question needs calculations on prices/volumes/options/holders, one agent (or you) loads `CORE_NOTES/data/*.csv` with python.

**Sweep-agent prompt template** (fill in the files and the question):
> Read these files IN FULL, sequentially from line 1 to the last line, with no skipping: <files> (all under C:\Users\palaz\Downloads\DKS_RESEARCH\). Question: "<user question verbatim>". Return EVERY fact relevant to the question: exact numbers with units and periods, dates, verbatim quotes with speaker, broker views, estimates, and contradictions between sources. Cite each item as (<notes file> › <SRC path>). Where a needed number is marked [r]/[sic] or looks inconsistent, verify it in the original file under SOURCE/ and say what you found. Also list anything that cuts AGAINST the obvious answer. No preamble; dense bullets; no word limit beyond what relevance requires.

**Step 3: Answer.** Synthesize from the digest and all agent returns:
- Lead with the direct answer, then the evidence.
- Cite sources compactly (notes file › source doc, date).
- Show how figures evolved over time (e.g. guidance by date) and flag conflicts between sources rather than picking one silently.
- Separate reported fact, management claim, broker or expert opinion, and your own inference (label inference).
- Use exact figures; state the period and fiscal-year convention.
- If the material doesn't cover something, say so plainly rather than filling the gap from general knowledge (or label any outside knowledge clearly as such).

**`quick:` mode** (only when the user's message starts with `quick:`): answer from the digest plus targeted Grep/Read of the notes, with no sweep agents.

## Rules
- Never edit or delete anything in `SOURCE/`, `CORE_NOTES/` or `WORKING_NOTES/` unless the user explicitly asks.
- The notes are complete by design: boilerplate (legal, disclaimers, safe-harbor, duplicate tables, transcript padding) was intentionally removed. Charts that were images in the original PDFs had no extractable values; the notes mark these as `[chart: …]`.
- Known source-data gaps (recorded in the notes): the DKS 8-K 2025-05-15 EX-99.3 Foot Locker investor presentation is image-only (no text); several UBS/BI/Needham figures are image-only; some JPM/Bloomberg-OCR table rows have uncertain column alignment (marked).
- Concurrency limit is 20 sub-agents at once.
