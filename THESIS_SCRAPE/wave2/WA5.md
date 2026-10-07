# WA5 (wave 2): Academy Sports (ASO) peer sweep: P_ASO_10K, P_ASO_10Q, P_ADIDAS_PUMA_ASO_FL_RESEARCH, plus ASO EDGAR history, ASO Q2 FY26 call and the ASO 2026 analyst-day deck
Agent WA5 | 2026-10-07 | Files read in full: P_ASO_10K.md (1-687), P_ASO_10Q.md (1-724), P_ADIDAS_PUMA_ASO_FL_RESEARCH.md (1-768). Then extended on the web: all 23 ASO 10-K/10-Qs (FY20-Q2 FY26) from EDGAR, the ASO Q2 FY26 call transcript (2026-09-09) and the ASO 2026 analyst-day deck (8-K 2026-04-07 EX-99.3, image-only, 58 slides).
Novelty check: I grepped the digest, primers (PRIMER_DENSE/READABLE), KNOWN_BRIEF and THESIS_SCRAPE\wave1 + wave2. Already known: the digest has ASO comps and valuation; the primer has ASO "~$13M year-1" new stores and 20-25 openings a year; wave-1 D01 has ASO opening sites; F5 has the JPM ASO sales/sq ft series; wave-2 WA1 has the DICK'S headcount series. Nothing in the folder or wave files covers the ASO base-cost, headcount, analyst-day or call data below (0 hits).
Variance constants: FY27E DSG revenue $15,203M (+3.05% vs FY26E $14,753M); 10bp of DSG margin = $15.2M = $0.124/sh; $1M pre-tax = $0.00814/sh.
Scripts: scripts\WA5_aso_filings.py (EDGAR headcount and labor text), scripts\WA5_aso_cost_model.py (cost series), scripts\WA5_news_rss.py and WA5_rss2.py (news RSS). Raw: raw\WA5_aso_headcount.csv, WA5_aso_filings.json, WA5_aso_sga_bridges.txt, WA5_aso_keyword_sentences.txt, WA5_aso_cost_series.csv, WA5_yahoo_aso_q2_transcript.txt, WA5_aso_analystday\ (58 slide JPGs + contact sheets).

## Top findings (ranked)

[WA5-1] **Academy, DKS's closest peer, has held its "base" SG&A flat in dollars for 9 straight quarters despite 3-4% wage inflation. In Q2 FY26 that base cost levered 130bp on a −0.4% comp.** This is the proof-of-concept that a big-box sporting-goods chain can take store and overhead cost out while comps are flat.

ASO base SG&A change y/y is total SG&A change minus company-stated "strategic investments" (new stores, tech, Jordan launch):

| | Q1FY24 | Q2FY24 | Q3FY24 | Q1FY25 | Q2FY25 | Q3FY25 | Q4FY25 | Q1FY26 | Q2FY26 |
|---|---|---|---|---|---|---|---|---|---|
| Base change ($M) | −3.8 | −1.0 | +1.8 | +2.8 | +8.9 | +3.1 | −3.0 | +3.6 | −4.0 |
| Base change (% of PY SG&A) | −1.1% | −0.3% | +0.5% | +0.8% | +2.4% | +0.8% | −0.8% | +0.9% | −1.0% |

- The 9-quarter average is about +0.2% a year.
- Total ASO SG&A growth fell from +10.2% (Q1FY25, its store-investment year) to +3.9% / +3.8% (Q1/Q2 FY26), with stores still +6.9% y/y.
- SG&A per average store y/y: Q3FY25 −0.2%, Q4FY25 −2.5%, Q1FY26 −3.4%, Q2FY26 −3.0%.
- The 10-Q bridge says SG&A +$15.2M = +$19.1M strategic investments, "partially offset by $3.9 million improvement in base costs".
- On the call, CFO Carl Ford said: "we leveraged base expenses by 130 basis points on a negative 0.4% comp". He attributed it to "corporate labor and recruiting and, you know, maintenance and repairs and third-party spend… professional fees", plus workers' comp and general liability, and "the team has managed healthcare costs well". He also said it is not "realistic that it's going to be 130 basis points on a slightly negative comp, but… if you do the math on what low single digit comps would mean, that gets to be really exciting".

| Q1FY24-Q2FY26 | 10-Q/10-K SG&A bridges via EDGAR (raw\WA5_aso_sga_bridges.txt; e.g. https://www.sec.gov/Archives/edgar/data/1817358/000181735826000149/ for the Q2 FY26 10-Q); call: https://finance.yahoo.com/markets/stocks/articles/academy-sports-aso-q2-2027-141319777.html (saved raw\WA5_yahoo_aso_q2_transcript.txt, lines 348, 457-458) | accessed 2026-10-07 | method: python on filing text; Q4FY25 and Q2FY25 strategic investment derived (FY 109.0 − 9M 85.0; 9M 85.0 − 33.4 − 24.7) | NEW (call quote and series); the single "$3.9M" sentence is BURIED in SOURCE\04_PEERS\ASO\sec_filings\ASO_10-Q_FY2026-Q2 l.965 | conf H (data), M (analogy) | SUPPORTS | thesis #2 | Variance: see the scenario table under WA5-2. The analog says a FY26 investment year can be followed by SG&A growth falling ~6pts within four quarters.

[WA5-2] **Academy cut store headcount per store ~21% since FY2020 and −10% y/y in 2026, lifting sales per team member +8.4% y/y. DICK'S went the other way. The "Built to Win" redesign has to close exactly this gap.**

ASO approximate team members (10-K/10-Q text) and period-end stores:

| Period end | ASO team members | ASO stores | Staff per store |
|---|---|---|---|
| FYE Jan-22 | 22,000 | 259 | 84.9 |
| FYE Jan-23 | 22,000 | 268 | 82.1 |
| FYE Feb-24 | 22,000 | 282 | 78.0 |
| FYE Feb-25 | 22,000 | 298 | 73.8 |
| Aug-25 | 23,000 | 306 | 75.2 |
| Nov-25 | 24,000 | 317 | 75.7 |
| FYE Jan-26 | 23,000 | 322 | 71.4 |
| May-26 | 22,000 | 324 | 67.9 |
| Aug-26 | 22,000 | 327 | 67.3 |

- In the year to Aug-26, headcount fell −4.3% while stores rose +6.9%, so staff per store fell −10.5% y/y.
- The full-time share fell from 50% (FY20-FY23 10-Ks) to 45% (FY24 and FY25 10-Ks): a deliberate shift to part-time flexibility.
- ASO sales per team member: FY21 $308K, FY22 $291K, FY23 $280K, FY24 $270K, FY25 $263K; LTM Aug-25 $260K, LTM Aug-26 **$281K (+8.4% y/y)**.
- DICK'S, using WA1's headcount (DICK'S Business year-end employees): sales per employee $234K (FY22), $234K (FY23), $240K (FY24), $236K (FY25), i.e. flat for four years. Employees rose +6.6% in FY25 against sq ft +1.6%. Staffing density is 1.31 employees per 1,000 sq ft vs ASO 1.05 (+25%). Some of that gap is structural: service-heavy HoS, GolfGalaxy fitting, and ~3x ASO's sales/sq ft.

| FY21-Aug-26 | scripts\WA5_aso_filings.py → raw\WA5_aso_headcount.csv (EDGAR CIK 1817358); scripts\WA5_aso_cost_model.py → raw\WA5_aso_cost_series.csv; DKS headcount from WA1-1 (W01/W02 10-K notes) | accessed 2026-10-07 | method: regex on filing text + arithmetic. ASO FY21/FY22 sales are from the 10-K MD&A ($6,773M / $6,395M), cross-checked against SG&A % disclosures | NEW (ASO series/comparison; the DKS series is WA1's) | conf M (ASO rounds headcount to the nearest 1,000, so ±2%; the Q2FY24 21,000 print looks like a rounding outlier) | SUPPORTS (proof that de-staffing is feasible in the category) / AGAINST (DKS has been moving the wrong way) | thesis #2

Variance (INFERENCE, DSG personnel; FY26E personnel ≈ 14.40% × $14,753M = $2,124M per D07):

| Scenario | FY27 personnel $ growth | FY27 personnel % | Δ vs FY26E | vs consensus* | $/sh vs consensus |
|---|---|---|---|---|---|
| A: redesign fails, run-rate only fades to +6% | +6.0% | 14.81% | +41bp | −41 to −51bp | −$0.51 to −0.63 |
| B: ASO-style SG&A deceleration only (personnel = sales +0.5pt) | +3.55% | 14.47% | +7bp | −7 to −17bp | −$0.09 to −0.21 |
| C: ASO-style base held flat; only new-format staffing adds | +1.5% | 14.18% | −22bp | +12 to +22bp | +$0.15 to +0.27 |
| D: ASO-style per-unit cut (staff/sq ft −3%, wage +3%, space +2.5%) ≈ flat $ → FY25 ratio | ~0% | 13.98% | −42bp | +32 to +42bp | +$0.40 to +0.52 |

\* Consensus FY27 DSG SG&A leverage is ~+22bp. D07-4's World Cup marketing roll-off (~10-20bp) can fund most of that, so consensus probably assumes personnel roughly flat-to-slightly-levered (0 to −10bp).

The key arithmetic: on +3.05% consensus revenue growth, personnel only levers if personnel dollars grow **below 3%**, against +9-10% in 1H FY26. ASO got there through per-unit cuts (headcount −4.3% with stores +6.9%), not through sales leverage. Thesis #2 therefore lives or dies on whether Built to Win removes hours or heads. The Q3 FY26 10-Q personnel line is the test.

[WA5-3] **Academy's 2026 long-range plan budgets only ~10bp a year of SG&A "sales leverage". That is a sobering benchmark against the ~+22bp of DSG SG&A leverage consensus already gives DKS for one year.** Analyst Day (2026-04-07), slide 48 "…While Generating EBIT Expansion", builds ~100bp of adj. EBIT margin over the LRP:

| Step | Adj. EBIT margin |
|---|---|
| 2025A | 9.0% |
| Sales leverage ("synergies associated with sales growth") | +0.5% |
| Supply-chain productivity | +0.5% |
| Retail media | +0.3% |
| Private label + softlines | +0.2% |
| Return value to customers | −0.5% |
| LRP target | 10.0% |

The plan assumes ~5% sales CAGR and LSD comps (CFO, Q2 call). The same deck (slide 24, "Delivers Operational Efficiencies") shows ASO "Piloting Digital Shelf Labels to Shift Labor to Customer-Facing", plus a team-member app and RFID/payment devices. That is a labor-reallocation toolkit similar to DKS's "AI in store labor forecasting".

| 2026-04-07 | https://www.sec.gov/Archives/edgar/data/1817358/000181735826000056/exhibit993-april2026anal048.jpg and …anal024.jpg (saved raw\WA5_aso_analystday\) | accessed 2026-10-07 | method: read slide images (exhibit is image-only) | NEW (not in SOURCE; the folder has no ASO 8-Ks) | conf H (figures) | AGAINST/NEUTRAL (the peer guides cost leverage slowly; ASO's actual 2026 base leverage beat this pace, see WA5-1) | thesis #2 | Variance: consensus's 22bp in a single year is ~2x ASO's entire 5-year "sales leverage" bucket. Upside vs consensus needs a cost program (Built to Win), not sales leverage.

[WA5-4] **Thesis #1 contrast: Academy's new-store engine adds only ~50bp of comp from 46-47 stores. On a rough INFERENCE, each HoS adds ~10x the comp dollars of an ASO new store, and ASO's new units are dilutive to productivity while HoS is accretive.**

ASO's own figures (Analyst Day slides 15/16/20; Q2 call):
- Year-1 sales: ~$16M in legacy markets (TX/OK/LA/AR), ~$14M in existing markets, ~$12M in new markets.
- Capital $2.5-3.5M per store; legacy-market payback ~2.5 years.
- 63 stores since FY22 = $1.1B sales; ~125 more planned in the LRP for +$1.9B.
- Urban Perimeter GA (2022) did ~$10M in year 1 vs rural Searcy AR (2024) ~$16.5M.
- Q2 call (Ford/Lawrence): the 46-47 stores opened 2022-25 that are in the comp base are "comping in the mid-single digits" and "contributed approximately 50 basis points to comp". This rises to 63 stores by YE FY26.
- Folder data (P_ASO_10K/10Q): new stores average ~$13M vs a chain average of ≈$19.5M (≈2/3).

INFERENCE:
- ASO: ~50bp ÷ 46 stores ≈ 1.1bp each × $6.05B ≈ **$0.65M of comp sales per new store per year**.
- DKS HoS: UBS ~150-170bp ÷ ~35 comp-base HoS ≈ 4.6bp × $14.1B ≈ **$6.5M per HoS**.
- WF puts HoS productivity at 124% of DSG; ASO new stores run at ~67% of its chain.
- FH (~$14M year-1, ~$4.5M net capex, ~2.5-yr payback) is economically an "ASO new store", with the added DKS twist that it replaces a ~$10-12M box.

| 2026-04-07 and 2026-09-09 | slides …anal015/016/020.jpg (URLs as above); transcript lines 335, 346, 353, 365, 425-426 | accessed 2026-10-07 | method: read + arithmetic | NEW (slides/call); the $13M average is DUP (primer) | conf M (the per-store comp math is rough: different comp definitions, ASO counts all 2022-25 openings) | SUPPORTS | thesis #1 | Variance: frames the HoS comp floor as unique in the category. The best-run value peer's growth engine yields ~50bp; DKS's relocation model yields 150-250bp. No new EPS number.

[WA5-5] **AGAINST (cost inflation): Academy's self-insurance charges (workers' comp, general liability, employee group health) jumped +21.6% in FY25.** The figures are $70.5M (FY23), $74.9M (FY24) and $91.1M (FY25), with ending reserves $25.0M → $25.2M → $29.2M; ASO's 401(k) match rose +7.6% ($15.7M → $16.9M). The CFO says these lines turned into a tailwind in 1H FY26 ("workers comp and general liability… providing benefit… managed healthcare costs well"). Read-across: FY25 claims and health inflation was real across the sector, consistent with DKS's "higher teammate healthcare costs" (Q2 FY26). ASO shows it can mean-revert within a year. | FY23-FY26 | P_ASO_10K.md › Schedule II (SOURCE\04_PEERS\ASO\sec_filings\ASO_10-K_FY2025_filed-2026-03-17.md) + Note 13; call line 458 | accessed 2026-10-07 | BURIED (Schedule II) + NEW (call) | conf H | AGAINST (FY25) / SUPPORTS (FY26 reversion) | thesis #2 | Variance: if DKS's FY26 healthcare spike mean-reverts like ASO's, every 10% of a ~$150-200M DICK'S health/claims line (INFERENCE; not disclosed) ≈ $15-20M ≈ 10-13bp ≈ $0.12-0.16/sh.

[WA5-6] **AGAINST (competitive service spend): Academy put part of its IEEPA tariff refunds into "incremental store labor and marketing" in Q2 FY26.** The CFO called it "testing and learning" in "some very select markets" and said "I would not bake that into the long-term algorithm" (transcript l.348, 349, 464). Tariff refunds net of the reinvestment were only +$0.06 to EPS. ASO also hired a new EVP and Chief People Officer (Matt Posh, ex-Burlington) in Sep-26 (l.488). Read: the main competitor is testing more store labor for service in its markets while DKS is redesigning labor for efficiency. This could pressure DKS to keep hours where it overlaps with ASO (Texas, Southeast). | 2026-09-09 | transcript (above) | NEW | conf M | AGAINST (mild) | thesis #2.

[WA5-7] **Foot Locker store wages per store rose +14% in two years (FY22-FY24).** These are the store wages of the business DKS now owns. Store employee wages were $849M / $861M / $862M on company-operated stores of 2,714 / 2,523 / 2,410, so per store $313K → $341K → $358K (≈ +6.9% a year). As % of revenue: 9.7% → 10.5% → 10.8%. FL's 2023 Investor Day bridge put wages at −1.0pt of EBIT. | FY22-FY24 | P_ADIDAS_PUMA_ASO_FL_RESEARCH.md › SRC 04_PEERS/FL/FL_Standalone_Financial_History_FY2019-FY2025_and_Lace_Up_Plan.md §3 "significant expenses" | method: arithmetic | BURIED (0 hits for "store employee wages" in digest/wave files) | conf H | AGAINST (FL segment wage inflation; a context point for consolidated SG&A, not the DSG thesis) | thesis #2 (context) | Variance: none for DSG. It supports treating store-labor productivity as a whole-company FY27 lever (FL ~$0.86B store wages).

[WA5-8] **Minor support for D07-4 (World Cup marketing was a one-off across the sector).** JPM Europe (21-Aug-26 Q2 wrap) attributes the brand EBIT misses partly to "one-offs incl World Cup investment". adidas Q2 26E marketing & POS was 13.0% of sales, +104bp y/y (Table 5, 2-Jul-26). The World Cup marketing spike was industry-wide and brand-funded, which fits DKS's adidas co-funded campaign rolling off in FY27. | Jul-Aug 2026 | P_ADIDAS_PUMA_ASO_FL_RESEARCH.md › SRC 04_PEERS/ADIDAS_PUMA/2026-07-07_JPMorgan… (Table 5) and 2026-08-26_JPMorgan… ("Opex: DTC growth comes with a cost") | BURIED | conf M | SUPPORTS (weak) | thesis #2 | Variance: none incremental (sizing is D07-4's).

## Smoking-gun candidates
1. **WA5-1 + WA5-2 together: "Academy already did it."** Over the last four quarters, the closest public peer:
   - cut headcount −4.3% while adding +6.9% stores (staff per store −10.5%);
   - held base SG&A flat in dollars for nine quarters;
   - levered base expense 130bp on a −0.4% comp, with its CFO on record.

   DKS over the same stretch grew DICK'S personnel +9-10% on sales +6%, and sales per employee has been flat at ~$235K for four years against ASO's $281K.

   The PM takeaway: the category's cost structure can be reset, the peer just proved it, and DKS has now announced and paid severance for its own version (Built to Win) without the Street crediting a dollar. It is hard, dated and verifiable (EDGAR + call transcript). The caveat: it is an analog, not DKS's own data. The Q3 FY26 10-Q personnel line is the DKS-specific proof.
2. **WA5-4 (thesis #1): the HoS comp contribution is ~10x the per-store comp yield of the best value peer's growth engine.** ASO's 46-47 new stores add ~50bp; ~35 HoS add ~150-170bp. It is a memorable framing, but built on rough INFERENCE math.

## Evidence against / caveats
- **The arithmetic is unforgiving.** At consensus FY27 DSG revenue growth of +3.05%, personnel only levers if personnel dollars grow below ~3%, against +9-10% in 1H FY26. Mere deceleration in ASO style (scenario B) still deleverages ~7bp and falls short of consensus. Upside needs real hours/head cuts (scenarios C/D).
- **ASO guides only ~10bp a year of sales leverage** in its LRP (WA5-3). The peer itself does not plan big structural SG&A leverage.
- **Structural differences:** DKS sells ~3x ASO's sales/sq ft and runs service-heavy HoS (~168 staff per HoS per WF) and GolfGalaxy fitting. The 1.31 vs 1.05 staff per 1,000 sq ft gap is not all waste.
- **ASO's per-store SG&A decline is flattered by new stores being smaller and lower-volume** (~$13M vs ~$19.5M average) and staffed leaner. That mix effect runs the opposite way at DKS, where HoS is larger and higher-staffed.
- **ASO headcount is rounded to the nearest 1,000** (±2%), and the timing of 10-Q snapshots matters for seasonal staffing.
- **Cost inflation:** ASO FY25 self-insurance +21.6% (WA5-5). FL store wages per store +6.9% a year (WA5-7). ASO is testing incremental store labor for service in shared markets (WA5-6).
- **ASO's 130bp base leverage includes corporate labor, professional fees and insurance**, not just store payroll. The store-labor-specific share is not disclosed.

## Avenue assessment
| Avenue | Access | Signal 1-5 | Script / path |
|---|---|---|---|
| Folder sweep (P_ASO_10K, P_ASO_10Q, P_ADIDAS_PUMA_ASO_FL_RESEARCH) | open | 3 | — |
| EDGAR ASO 10-K/10-Q history (headcount, FT/PT, SG&A bridges) | open (one transient reset) | 5 | scripts\WA5_aso_filings.py; raw\WA5_aso_headcount.csv, WA5_aso_sga_bridges.txt |
| ASO Q2 FY26 call transcript (Yahoo, via requests) | open (Benzinga 403; WebFetch timed out on Yahoo; python requests worked) | 5 | raw\WA5_yahoo_aso_q2_transcript.txt |
| ASO 2026 Analyst Day deck (8-K EX-99.3, image-only JPGs) | open | 4 | raw\WA5_aso_analystday\ (+ contact sheets) |
| Google/Bing News RSS | open (Google intermittently SSL-EOF; its article links are JS-redirect encoded) | 2 | scripts\WA5_news_rss.py, WA5_rss2.py; raw\WA5_news_rss.json |
| ASO Q4 FY25 / Q1 FY26 transcripts | partial (only Google-encoded links found; not retrieved) | — | — |

## Leads for next wave
- **ASO Q1 FY26 (2026-06-09) and Q4 FY25 (2026-03-17) call transcripts.** Try Yahoo slugs of the form finance.yahoo.com/markets/stocks/articles/academy-sports-aso-q1-2027-… (the Q2 slug was "academy-sports-aso-q2-2027-141319777") or Investing.com. Look for base-cost bps and labor-model comments to extend WA5-1 to three quarters.
- **ASO Q3 FY26 10-Q/call (~2026-12-08).** Check whether base-cost leverage persists. It lands ~2 weeks after DKS Q3 (Nov 24-25). Compare DKS Q3 personnel % y/y with the ASO base-cost line side by side.
- **ASO 10-K FY26 (Mar-2027):** team members and FT/PT split. If ~22,000 on ~345 stores, staff per store ~64.
- **DKS Q3 FY26 10-Q segment note:** DICK'S personnel $ growth vs +3% (the scenario threshold in WA5-2).
- **ASO analyst-day slides 16-18 and 44-47** (saved) for any further store-level metrics. Slide 20 states legacy-market payback ~2.5 years.
- Other peers with hard store-labor disclosures to pair with ASO: Hibbett (inside JD), Big 5 (private), Sportsman's Warehouse (SPWH 10-K "store payroll" commentary and its 2024-25 cost-out program). Use EDGAR full-text search for "store payroll" in SPWH 10-Q 2025-2026.

## Dead ends / blocked
- Benzinga transcript: HTTP 403. WebFetch on Yahoo timed out (python requests worked).
- Google News RSS links are JS-encoded redirects that cannot be resolved without a browser. Google RSS also intermittently threw SSL EOF errors; Bing RSS worked.
- The ASO analyst-day exhibit has no text layer (images only); the values were read visually from slides 15, 20, 24 and 48.
- No ASO statement anywhere quantifies store payroll specifically (ASO reports a single SG&A line; payroll is not split).

Duplicates skipped: ASO comps 2024-Q2 FY26 and transactions (digest); ASO "~$13M year-1" new stores, 20-25 openings, Jordan/HOKA at Academy (primer); ASO opening sites and satellite markets (D01, primer); ASO sales/sq ft (F5); ASO Q3 QTD LSD comp (D06); DKS DICK'S headcount series (WA1); IEEPA refund mechanics; FL Lace Up targets/closures (excluded); ASO buybacks/debt (excluded or irrelevant).

STATUS: COMPLETE
