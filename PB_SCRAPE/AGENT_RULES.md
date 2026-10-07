# AGENT RULES: DKS owned-brand scrape (read fully before doing anything)

## Mission
The user is pitching DICK'S Sporting Goods (DKS) as a buy-side analyst. They want NOVEL, substantive, sourced evidence that DKS's OWNED / VERTICAL brands (DSG, CALIA, VRST, MAXFLI/Maxfly, Walter Hagen, Top-Flite, Tommy Armour, Alpine Design, ETHOS, Fitness Gear, Nishiki, Quest, + any other DKS-owned brand you discover) have been ACCELERATING over roughly the last six months (about Apr-Oct 2026, versus the same months of 2025 and the longer history). The point is to justify modelling owned-brand mix of DICK'S Business sales rising faster than consensus implies. Consensus has no explicit mix line: it implicitly assumes about 13% that's flat, and Bloomberg DSG GM is ~36.2-36.3% flat FY25A-FY27E. The user also wants to know the BEST, repeatable avenues for scraping such data.
- DKS owned brands ONLY (not Foot Locker private label, not licensed brands like adidas football/Cobra/Marucci/Lotto, though note if licensed deals are expanding).
- Today is 2026-10-07. DKS FY2026 = year ending 2027-01-30. Q2 FY26 ended 2026-08-01; Q3 FY26 ends 2026-10-31.

## Novelty rule (most important)
1. Read `C:\Users\palaz\Downloads\DKS_RESEARCH\PB_SCRAPE\KNOWN_BRIEF.md` first. Anything in it is already known: do not report it as a finding.
2. Before recording any finding, Grep for its key number/term across `CORE_NOTES\`, `WORKING_NOTES\`, `FL_EUROPE_SCRAPE\baseline\primers\` and `PB_SCRAPE\wave*\` (other agents' output). Tag it:
   - `NEW`: not anywhere in the folder.
   - `BURIED`: in the folder notes, but not in KNOWN_BRIEF/primers (folder agents mostly). Give the file › SRC path.
   - `DUP`: already known. Drop it, or list it in one line under "Duplicates skipped".
3. A restatement of the known 13% / $1.8B / 700-900bps / "#2 vendor" / "outperforming" is NOT a finding. New numbers, new dated observations, new time series and new sources ARE findings.

## Quality bar
- Quantitative time series > dated datapoints > qualitative quotes > anecdotes. Prefer anything that shows CHANGE over time (2025 → 2026, monthly).
- Every number needs its source URL (or file path), the date you accessed it, and the method. Never fabricate or estimate silently. Label inference as `INFERENCE`.
- Also record evidence that cuts AGAINST the thesis (flat/declining mix, weak reviews, discounting of owned brands, Stack's "never super high" comment confirmed, etc.). The user needs the honest picture.

## Tools & access
- WebSearch / WebFetch are deferred tools: load them first with ToolSearch query `select:WebSearch,WebFetch`. Use WebSearch mode "standard" by default, "extended" for hard/niche/recent items.
- NOTE (05:30 CDT): the Apify ACCOUNT has hit its monthly hard limit, so Apify is unavailable. Do not try Apify actors. Use free routes only (public APIs, Bazaarvoice, Common Crawl, ImportYeti free pages, USPTO, EDGAR, Wayback, RSS).
- NOTE (03:55 CDT): the session's WebSearch quota may be EXHAUSTED. If WebSearch errors out or refuses, do not stop. Use these fallbacks: (1) WebFetch or python requests on `https://html.duckduckgo.com/html/?q=<query>` or `https://www.bing.com/search?q=<query>` and parse the result links; (2) Apify `apify/rag-web-browser` with a search query (cheap; count it against the budget); (3) go directly to known site search pages / APIs / sitemaps / RSS (Google News RSS: `https://news.google.com/rss/search?q=<query>`).
- Python 3.13 is installed with requests + beautifulsoup4. You may `pip install` well-known PyPI packages (pandas, pytrends, curl_cffi, lxml, waybackpy) if needed. Shell is Windows PowerShell 5.1 (no `&&`).
- Apify (paid scrapers) only if your assignment gives you an Apify budget. Load the tools with ToolSearch `+Apify`. Before each run, read `PB_SCRAPE\APIFY_LEDGER.md`. Never let the ledger total exceed $25.00, and never exceed your own budget. After each run, append a line: `date | agent | actor | run id | est cost $`. Prefer cheap actors, set small maxItems, and check pricing in actor details first.
- Only agent X02 may use the built-in browser tools (mcp__Claude_Browser__*). Everyone else must not, to avoid collisions.
- PROHIBITED: solving CAPTCHAs or bypassing bot-detection challenges; logging in; creating accounts; submitting forms; entering any credentials; purchases; downloading/executing untrusted files. If a site blocks you, try legitimate alternatives (public JSON/API endpoints the page itself calls, sitemaps, Wayback Machine, Google cache/search snippets, Apify actors), then log it as blocked and move on.
- Never edit anything in SOURCE\, CORE_NOTES\, WORKING_NOTES\.

## Output (write incrementally so progress survives a crash)
- Create your output file IMMEDIATELY at `PB_SCRAPE\wave<N>\<ID>.md` with a header and `STATUS: IN PROGRESS`. Append findings as you go, and at least every ~20 minutes of work.
- Raw data → `PB_SCRAPE\raw\<ID>_<name>.(csv|json|txt)`. Reusable scripts → `PB_SCRAPE\scripts\<ID>_<name>.py`, with a docstring explaining how to rerun.
- Final file structure:
  1. `## Top findings` (ranked). Each one: `[ID-n] finding with exact numbers | period | source URL/path | accessed date | method | NEW/BURIED | confidence H/M/L | SUPPORTS/AGAINST/NEUTRAL | how to use it in the model`
  2. `## Evidence against / caveats`
  3. `## Avenue assessment`: for each avenue tried: accessibility (open/partial/blocked), cost, refresh frequency, signal quality 1-5, script path, and how a human analyst could run it weekly
  4. `## Leads for next wave`: specific URLs, endpoints, queries, names
  5. `## Dead ends / blocked`
  6. Last line exactly: `STATUS: COMPLETE`
- Work until your avenue is genuinely exhausted. Depth beats breadth. If your avenue turns out to be blocked, pivot to the closest adjacent avenue that could produce the same kind of evidence, and say so.
- Your final reply to the orchestrator: ≤250 words covering the 3-5 best findings, your output file path, the best leads, and Apify $ spent.
