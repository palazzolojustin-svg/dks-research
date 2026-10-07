# AGENT RULES: DKS two-thesis overnight scrape (read fully before doing anything)

## Mission
The user is pitching DICK'S Sporting Goods (DKS) long as a buy-side analyst (Point72 Academy style). They need HARD, NOVEL evidence that creates clear VARIANCE versus Bloomberg consensus for two long thesis points, plus a "smoking gun" (one novel, compelling piece of evidence) for each:
- THESIS #1: House of Sport (HoS) / Field House (FH) new formats give DKS a structural comp floor and high returns that consensus under-models. Consensus core comp is only ~1.6-2.4% for 3Q26E-2Q27E, versus a store-format contribution alone of ~150-250bps. Wave 1 showed that consensus therefore implies roughly ZERO or NEGATIVE underlying comp for the rest of the fleet (vs ~+2.8-3.4% actual over the last 8 quarters and +1.2% in the bear Wells Fargo model). Evidence we want: proof that HoS/FH stores generate MORE sales and traffic than modelled, ramp faster, cannibalize less, or lift the surrounding store base, and proof that the legacy fleet is still comping positive, plus anything that rebuts the "underlying comp is weak" bear case.
- THESIS #2 (chosen after wave 1): FY27 core store-cost reset. DKS's "Built to Win" store labor redesign (announced 2026-04-14, $15.3M Q2 FY26 severance/training charge, savings never quantified) plus FY26 one-off costs rolling off (World Cup marketing, Fort Worth DC start-up, pre-opening timing) → DICK'S segment SG&A/personnel leverage in FY27 above the ~+29bp margin expansion consensus already assumes. Evidence we want: proof the redesign cut store labor hours/cost (de-layering, fewer managers, hours cuts, lower payroll per store), the size of comparable programs at other retailers, wage-rate trends, and anything showing the 1H FY26 personnel deleverage (+44bp) is temporary, plus evidence against (higher pay rates, HoS staffing intensity, healthcare).
Today is 2026-10-07. DKS FY2026 = year ending 2027-01-30 (Bloomberg "2027 Y"). Q3 FY26 = Aug-Oct 2026, reported ~Nov 24-25, 2026.

## Hard exclusions
Do not research owned/vertical/private brands, buybacks, FL store closures, or FL divestiture/international exit. Do not read from or write to PB_SCRAPE\ (a separate run) except to Grep it for novelty checks.

## Novelty rule (most important: the user explicitly does NOT want evidence we already have)
1. Read `C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\KNOWN_BRIEF.md` first. Anything in it is already known: do not report it as a finding.
2. Before recording any finding, Grep its key number/term across `CORE_NOTES\00_CORE_DIGEST.md`, `FL_EUROPE_SCRAPE\baseline\primers\` (the user's existing primers) and `THESIS_SCRAPE\wave*\` (other agents' output, including wave 1). Then tag it:
   - `NEW`: not in the folder at all (web-sourced, or computed fresh from raw data).
   - `BURIED`: in CORE_NOTES/WORKING_NOTES/SOURCE detail but NOT in the digest, the primers, KNOWN_BRIEF or earlier wave files (never surfaced to the user). Give file > SRC path. These count as novel.
   - `DUP`: already in the digest, primers, KNOWN_BRIEF or an earlier wave file. Drop it, or list it in one line under "Duplicates skipped". (Building on a wave-1 finding with NEW data is fine; say which finding you extend.)
3. Restating known numbers is NOT a finding. New numbers, new dated observations, new time series, new sources and fresh calculations ARE findings.

## Quality bar
- Hard evidence beats opinion: quantitative time series > dated datapoints > documents (permits, filings, minutes) > quotes > anecdotes. Prefer evidence that shows CHANGE (2025 to 2026) or a comparison (HoS vs legacy store, DKS vs peers).
- Every number needs its source URL (or file path + SRC), the access date and the method. Never fabricate. Label your own estimates `INFERENCE` and show the arithmetic.
- For each finding say how it converts into variance: comp bps vs the consensus revenue estimate, margin bps vs the consensus margin, then $/share (FY27E: 89.09M shares, 27.46% tax; DKS segment revenue $15,203M, segment OI $1,647M = 10.83% margin vs FY26E 10.54%; 10bp of DSG margin = $15.2M = $0.124/sh; $1M pre-tax = $0.00814/sh).
- Also record evidence that cuts AGAINST the thesis. The user needs the honest picture.

## Tools & access
- APIFY IS UNAVAILABLE (account monthly hard limit hit). Do not call Apify. WebSearch hit a 200-call session cap in wave 1: you may try it (≤10 calls per agent), but if it errors, switch immediately to the fallbacks below.
- Search fallbacks that work: Python requests to Bing News RSS (https://www.bing.com/news/search?q=<query>&format=rss), Google News RSS (https://news.google.com/rss/search?q=<query>&hl=en-US&gl=US&ceid=US:en), SEC EDGAR full-text search (https://efts.sec.gov/LATEST/search-index?q="<phrase>"&dateRange=custom&startdt=2025-01-01, User-Agent header with an email), Reddit public JSON (https://www.reddit.com/r/<sub>/search.json?q=<q>&restrict_sr=1&sort=new, with a descriptive User-Agent), Wayback CDX (http://web.archive.org/cdx/search/cdx?url=...), public government APIs (BLS, Census, state open-data/Socrata, state WARN pages), the DKS IR JSON feed (investors.dicks.com/feed/PressRelease.svc/GetPressReleaseList...). Load WebFetch with ToolSearch `select:WebFetch` and use it on URLs you find. DuckDuckGo and Similarweb return bot challenges: do not use them.
- If anything returns a CAPTCHA/challenge, stop using that source (do not bypass it).
- Python 3.13 is installed with requests + beautifulsoup4. You may `pip install` well-known PyPI packages (pandas, feedparser, lxml, waybackpy, pdfplumber) if needed. Shell is Windows PowerShell 5.1 (no `&&`). Data CSVs live in CORE_NOTES\data\.
- Do NOT use any browser tools (mcp__Claude_Browser__* or claude-in-chrome); another run uses the browser.
- PROHIBITED: solving CAPTCHAs or bypassing bot-detection; logging in; creating accounts; submitting forms; entering credentials; purchases; downloading/executing untrusted executables. Public PDFs (city minutes, filings) are fine to fetch and parse. If a site blocks you, try legitimate alternatives, then log it as blocked and move on.
- Never edit anything in SOURCE\, CORE_NOTES\, WORKING_NOTES\, PB_SCRAPE\.

## Output (write incrementally so progress survives a crash)
- Create your output file IMMEDIATELY at `THESIS_SCRAPE\wave<N>\<ID>.md` with a header and `STATUS: IN PROGRESS`. Append findings as you go, at least every ~20 minutes of work.
- Raw data to `THESIS_SCRAPE\raw\<ID>_<name>.(csv|json|txt)`. Reusable scripts to `THESIS_SCRAPE\scripts\<ID>_<name>.py`, with a docstring saying how to rerun.
- Final file structure:
  1. `## Top findings` (ranked). Each one: `[ID-n] finding with exact numbers | period | source URL/path | accessed date | method | NEW/BURIED | confidence H/M/L | SUPPORTS/AGAINST/NEUTRAL | thesis #1/#2 | variance translation`
  2. `## Smoking-gun candidates`: the 1-3 findings most likely to be the single novel, hard piece of evidence a PM would remember, and why.
  3. `## Evidence against / caveats`
  4. `## Avenue assessment`: each avenue tried, with accessibility (open/partial/blocked), signal quality 1-5 and the script path
  5. `## Leads for next wave`: specific URLs, endpoints, queries, names
  6. `## Dead ends / blocked`
  7. Last line exactly: `STATUS: COMPLETE`
- Work until your avenue is genuinely exhausted. Depth beats breadth. If your avenue is blocked, pivot to the closest adjacent avenue that could produce the same kind of evidence, and say so.
- Your final reply to the orchestrator: 250 words or fewer, covering the 3-5 best findings, your output file path and the best leads.
