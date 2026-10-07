# AGENT SPEC: converting DKS research sources into notes for Claude to read (not humans)

ROOT = `C:\Users\palaz\Downloads\DKS_RESEARCH` (always use absolute paths: ROOT\...)
Your assignment (id, output path, files, note) is in `ROOT\_PREP\assignments.json`; find the entry whose "id" matches yours.

## Objective
Produce notes that preserve **every distinct piece of information** in your assigned sources while removing only:
(a) file/format overhead (markup, page markers, headers/footers, garbled whitespace, PDF metadata blocks),
(b) legal boilerplate (forward-looking/safe-harbor language, SEC cover-page checkboxes, signature blocks, generic GAAP policy text that is not company-specific, XBRL/tag noise, table of contents, standard exhibit index entries),
(c) standard disclaimers (broker disclosures, analyst certifications, rating definitions/distributions, regulatory and copyright notices, "important information" pages),
(d) a table or passage repeated verbatim or near-verbatim (write it once; afterwards write `=same as <SRC id/section>` and record only what differs),
(e) transcript padding (operator lines, greetings, thanks, "great question", filler, repeated restatements of the same point by the same speaker).
**Everything else stays**: every number, period, unit, name, date, guidance item, KPI, reason, causal claim, opinion, caveat, risk, quote, estimate, rating, price target, survey/alt-data datapoint, footnote with substance, company-specific accounting judgment, legal proceeding, contract term, covenant, deal term, store count, segment data, etc. If unsure whether something is boilerplate → KEEP it (densely).

## Reading rules (every word must be processed)
1. Read each assigned input in sequential chunks with the Read tool (offset/limit, e.g. 300–800 lines per call) from line 1 to the last line. Never skip a range. For a `line_range` entry, read exactly that range.
2. If an entry has `read_delta`, read that delta file in full INSTEAD of the original: it holds every line of the original that is not a verbatim repeat of the reference document (which another pass covers). Open the original around the listed line numbers whenever you need context (e.g. table headers). Record in your notes what is new/different vs the reference, including ALL prior-period comparative figures.
3. If a line appears truncated in Read output, print it with python (`python -c "..."`) to see it in full.
4. CSV inputs: inspect with python (pandas is fine). Follow the assignment note.
5. You may skim disclosure/disclaimer pages quickly, but confirm they contain no company-specific content before dropping them (broker disclosure pages sometimes contain the company's rating history/PT history: KEEP that).

## Output format (dense, for a machine reader)
- Write per-source part files to `ROOT\_PREP\parts\<ID>\NN.md` (NN = 01, 02, … in assignment order) as soon as each source is done, so work survives context compaction. When all sources are done, concatenate them into the assignment's `output` path (python), preceded by a header:
  ```
  # <ID> | <short title>
  > SOURCES: <n> files | fiscal note if relevant (e.g. DKS FY2025 = FYE 2026-01-31) | legend: [d]=derived by note-writer, [r]=table rebuilt from garbled PDF text, =same as=duplicate pointer
  ```
- Each source section starts with: `## SRC <path relative to ROOT/SOURCE> | <document date> | <doc type / firm / author / speakers> | <period covered>`
- Body: terse bullets. Standard finance shorthand (rev, GM, SG&A, EBIT, OI, EPS, comp, y/y, q/q, bps, mgmt, gdnc, cons, PT, OW/UW, FCF, capex, inv, DTC, wholesale, ASP, AUR, sq ft…). Drop articles and filler. Semicolon-chain related facts. Group under short `###` topic headings.
- Numbers: exactly as in source (no rounding), with unit and period. Never invent, never "approximately" unless the source says it. Mark your own arithmetic `[d]` (keep it minimal).
- Tables: compact pipe tables with every row and column. Rebuild PDF tables printed one cell per line (mark `[r]`). If a table cannot be rebuilt reliably, write `[garbled table, p.X] values in order: ...` and list all values.
- Quotes: keep verbatim (in "quotes", attributed `—Name, Title/Firm`) for guidance, outlook, strategy, tone/hedging, quantified claims and anything an investor would want exact wording for. Paraphrase everything else densely, keeping every distinct claim.
- Transcripts: prepared remarks as topic bullets; Q&A as `Q [Analyst, Firm]: <question incl. numbers>` then `A [Speaker]: <every distinct point>`.
- Broker research: header line with firm, analyst, date, rating (old→new), PT (old→new, basis), price at publication; then thesis, estimate changes (old→new vs cons), model tables, valuation method/multiples, bull/bear/base cases, catalysts, risks, alt-data/survey/channel-check datapoints, any DKS read-through (always flag DKS read-through in peer notes with `DKS-READ:`).
- Expert calls: expert role/company type/date; every claim with numbers; verbatim key quotes; who said what (expert vs interviewer).
- SEC filings: financial statements and segment tables in full (all periods shown); MD&A drivers with every number; risk factors condensed to their specific substance (keep every company-specific risk, drop generic phrasing); notes to financials (debt terms, leases, tax, SBC, buybacks, dividends, contingencies, subsequent events); exhibits listed only if material.
- No commentary, no conclusions of your own beyond `[d]` arithmetic.

## Size guidance
Remove redundancy, not information. Prose usually compresses to ~20–40% of its original characters; tables compress little. Never drop a fact to save space.

## Coverage manifest (required)
Write `ROOT\_MANIFEST\coverage\<ID>.tsv` with a header row and one row per assigned input:
`source<TAB>mode(full|delta|lines a-b)<TAB>total_lines<TAB>last_line_read<TAB>dropped_as_boilerplate(short description)<TAB>output_file<TAB>notes_chars_for_this_source`

## Constraints
- Do NOT modify anything under ROOT\SOURCE. Write only to your part folder, your output file and your manifest row file.
- Do not spawn sub-agents or workflows.
- Final reply (≤8 lines): output path, total chars, per-file status (all read to last line? Y/N), any problems (unreadable sections, unrebuildable tables).
