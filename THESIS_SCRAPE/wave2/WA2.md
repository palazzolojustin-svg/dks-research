# WA2 (wave 2): sweep of W03 (DKS 10-Qs Q3 FY22 to Q3 FY24), W06 (debt and registration docs), W08 (Foot Locker deal 425 communications)
Agent WA2 | 2026-10-07

**Files read in full:**
- W03_DKS_10Q_FY22Q3-FY24Q3.md (lines 1-1122)
- W06_DKS_DEBT_REGISTRATION_DOCS.md (1-283)
- W08_DKS_FL_DEAL_COMMUNICATIONS_425.md (1-171)

**Novelty check.** I Grepped each key term and number against CORE_NOTES\00_CORE_DIGEST.md, FL_EUROPE_SCRAPE\baseline\primers\*, KNOWN_BRIEF.md and THESIS_SCRAPE\wave1\* plus wave2\*. The terms checked were "business optimization", "84.8", "72.8", "customer support center", "largely offset", "hourly wage", "wage rate", "corporate & other", "unallocated", "1,869", "1,838", "Germano" and "payroll system".

**Script:** THESIS_SCRAPE\scripts\WA2_2023_optimization_analog.py writes raw\WA2_2023_analog.csv.

**Spot-checks in SOURCE:**
- 8-K 2023-08-22 (Item 2.05)
- 10-Q FY2023-Q2 (l.773, l.788)
- 10-Q FY2023-Q3 (l.782)
- 10-K FY2023 (l.982)

**Variance constants:** FY27E DSG revenue $15,203M; 10bp = $15.2M = $0.124/sh; $1M pre-tax = $0.00814/sh.

**Overlap warning.** WA1 reads the same 10-Ks (W01/W02), so it may also surface the 2023 Business Optimization. My unique additions are:
- the 10-Q guidance trail;
- the Q4 FY23 check against that guidance;
- the "savings reinvested" 8-K language;
- proof that the FY23 personnel line and the FY26 redesign charge both sit outside segment personnel;
- the analog arithmetic.

## Top findings (ranked)

[WA2-1] **DKS has done this before: a 2023 severance-backed cost action is the closest precedent for "Built to Win". In the year after it, the DICK'S personnel line levered, but management reinvested the savings and total SG&A did not lever.**

What happened in 2023:
- On 2023-08-21/22 DKS "eliminated certain positions primarily at our customer support center", expecting ~$20M of severance (8-K Item 2.05, 2023-08-22).
- The final FY23 "Business Optimization" charge was **$84.8M**: $26.7M severance, $46.1M non-cash store and intangible impairments (Moosejaw/outdoor) and a $12.0M inventory write-down. Of this, $72.8M sat in SG&A ($46.2M in Q3, ~$26.6M in Q4).

What management guided, in order:
1. Q2 FY23 10-Q: SG&A "over 200 basis points higher than fiscal 2022" for the rest of the year. On savings, the 8-K and 10-Q said verbatim: **"Related cost savings are expected to be largely offset by strategic talent investments over the next twelve months."**
2. Q3 FY23 10-Q: SG&A to "moderate by approximately 150 basis points from the third quarter as a percentage of net sales, following our business optimization actions."
3. 10-K FY23: SG&A "moderated by approximately 78 basis points" in Q4, and "In 2024, we expect selling, general and administrative expenses to leverage... driven by the future benefits from our Business Optimization actions."

What actually happened (my calculation):
- **Q4 FY23 versus the guide.** Implied Q4 SG&A was 24.73% of sales vs 25.51% in Q3, a 78bp moderation. Excluding the ~$26.6M of Q4 optimization charges it was **24.04%, which hits the ~150bp guide (≈24.01%) almost exactly.**
- **FY24 personnel (DICK'S CODM table).** Personnel rose only **+1.7% (+$30.7M, to $1,869.3M)** on sales +3.5%, after +12.5% (+$204.0M) in FY23. As a share of sales it went from 14.16% to 13.91% (−25bp). On a 52-vs-52-week basis it is about **−17bp** (personnel +3.6% vs sales +4.9%; this assumes the 53rd week's personnel was pro rata).
- **FY24 personnel versus a sales-growth path.** Personnel came in **$23-34M below** where it would have been had it grown with sales. That is **0.87-1.28x the $26.7M severance**, and it happened even though FY24 incentive comp was higher.
- **FY24 total SG&A.** Total SG&A ex-charges *deleveraged* +55bp (23.96% → 24.51%), or ~+48bp ex the deferred-comp swing. "Other segment expenses" rose from 15.40% to 15.79% of sales. Segment margin still rose 10.64% → 11.14%, but that came from gross margin (+98bp).

Sources and tags:
| FY22-FY25 | W03 › SRC 10-Q FY2023-Q2/Q3, FY2024-Q1/Q2/Q3; W06 › SRC 424B2 2026-09-22 (non-GAAP recon: FY23 business optimization $84,813K); W01 › 10-K FY25 Note 17 / FY24 Note 16; verified in SOURCE (8-K 2023-08-22 l.95; 10-Q FY23Q2 l.773/788; 10-Q FY23Q3 l.782; 10-K FY23 l.982) | accessed 2026-10-07 | method: read + python (scripts\WA2_2023_optimization_analog.py) | BURIED: the digest has only "~$20M severance" on the 2023-08-22 guide-cut row (l.118); the $84.8M composition, the "largely offset" language, the guidance trail and the FY24 personnel outcome appear in no digest, primer or wave file | conf H on the data, M on the analog | SUPPORTS (personnel did lever after the last action; management hit its SG&A guide) and AGAINST (savings were explicitly reinvested; total SG&A ex-charges deleveraged) | thesis #2

Variance translation (INFERENCE):
- If Built to Win (~$21M FY26 charge) yields year-1 personnel savings at the 2023 ratio (0.87-1.28x the charge), that is **$18-27M ≈ 12-17bp of FY27 DSG margin ≈ +$0.15-0.22/sh gross.**
- Consensus already assumes ~+22bp of DSG SG&A leverage. The 2023 precedent says DKS reinvests savings. So the net variance vs consensus is positive only if FY27 non-personnel SG&A is held flat as a share of sales, which is the opposite of what happened in FY24.
- The pitch should therefore frame Built to Win as "personnel lever proven in FY24 (−17 to −25bp), and management hit its post-action SG&A guide to the basis point". It should not claim margin upside that is fully additive.

[WA2-2] **The Q2 FY26 redesign charge is NOT in the DICK'S segment personnel line. It sits in "Corporate & other", exactly as the 2023 severance did. So the +43-45bp personnel deleverage in 1H FY26 is underlying run-rate cost, not severance, and the "training" cost is also excluded.**
- 10-Q FY26 Q2 segment note: Corporate & other Q2 expense = "$29.3M FL acquisition costs + $15.3M DICK'S store operating model redesign, offset $38.1M prior-year IEEPA refunds; deferred comp +$6.1M".
- The 2023 precedent is identical. The FY25 10-K recast puts FY23 "corporate & other" at $98,773K = $84,813K business optimization + $13,960K deferred comp (reconciles exactly). The FY23 personnel figure ($1,838.6M, 14.16%) is therefore also clean of severance. That means the FY23 +94bp step was pure wage, talent and incentive cost (see WA2-3).

Implications:
- (a) A bear cannot say the 1H26 personnel deleverage is inflated by severance. Equally, a bull cannot say it will "fall away" when the charge ends.
- (b) The Q3 FY26 10-Q personnel line (early Dec) is a clean test of Built to Win savings net of transition costs.
- (c) Because the training costs ("severance, training and other") are excluded, any double-staffing during rollout that was booked as training does not depress the segment line.

| Q2 FY26; FY23 | W04 › 10-Q FY26Q2 Note 7 (l.1105, l.1192); W01 › 10-K FY25 Note 17 (corporate & other 98,773) + W06 › 424B2 non-GAAP recon (84,813) | accessed 2026-10-07 | method: read + reconciliation | BURIED ("corporate & other" / "unallocated" = 0 hits in digest/primers/wave files; D07/F6 did not say where the charge sits) | conf H | NEUTRAL (sharpens the test; makes the deleverage "real") | thesis #2 | variance: none direct. It removes a false bull argument and validates using the segment personnel line as the scorecard.

[WA2-3] **The 2022-23 store-wage reset was a discrete, management-attributed, two-year step. Personnel then held flat for two years, so the 1H FY26 +44bp is the first new step since.**

SG&A growth that MD&A attributed to "hourly wage rates, talent, technology":
| Period | $ |
|---|---|
| FY22 | +$127.1M (partly offset by lower incentive comp) |
| Q1 FY23 | ~+$68.6M ($78.6M less $10.0M deferred comp) |
| Q2 FY23 | +$51.5M |
| Q3 FY23 | +$33.7M (with marketing) |
| Q4 FY23 implied | ~+$51.8M |
| FY23 total | **+$191.7M** (plus $66.0M marketing) |

- The words "hourly wage rates" first appear in Q3 FY22 ("SG&A ... on hourly wage rates, talent, technology investments").
- They disappear from MD&A in FY24. FY24 drivers became "incentive comp, brand-building marketing, other costs supporting growth" (Q1 FY24 +$46.0M; Q2 +$31.9M; Q3 +$22.4M).
- Personnel $ growth: FY23 +12.5%, FY24 +1.7%, FY25 +5.5%, 1H FY26 ~+9.4%. As a share of sales: 13.22 → 14.16 → 13.91 → 13.98%.
- Read-across (INFERENCE): DKS's personnel ratio moves in episodic, management-chosen steps (FY23 wage reset, now the FY26 model redesign plus HoS staffing). It has never mean-reverted on its own: the FY23 step held. So FY27 leverage needs Built to Win to actually cut hours.

| Q3 FY22-Q3 FY24 | W03 › SRC 10-Q FY2022-Q3 to FY2024-Q3 MD&A; W02 › 10-K FY22/FY23 MD&A (cross-check) | accessed 2026-10-07 | method: read + sum | BURIED (the "hourly wage"/"wage rate" terms = 0 hits; only the annual ratios are known) | conf H | NEUTRAL/AGAINST (no automatic mean reversion; the FY23 step never reversed) | thesis #2 | variance: none direct. It frames the base rate: absent action, personnel % is sticky.

[WA2-4] **The 2023 action also shows DKS management's post-restructuring SG&A guidance has been reliable on timing. And the Q2 FY24 quarter shows what SG&A leverage looks like at a ~4.5-5% comp.**
- Q2 FY24: SG&A $ +4.2% on sales +7.8% (+4.8% ex the ~$95M calendar shift), for 79bp of reported leverage. 1H FY24 SG&A levered 33bp (23.72% vs 24.05% recast).
- Q1 FY24 SG&A grew +7.1% vs sales +4.6% ex-shift (incentive comp), and Q3 FY24 grew +2.9% (lapping $46.2M of charges).
- So the "post-action" leverage came in the second and third quarters after the cut, not the first.

| FY24 | W03 › SRC 10-Q FY2024-Q1/Q2/Q3 | method: python | BURIED (the quarterly SG&A y/y series is not in the digest) | conf H (calendar-shift amounts are management's) | SUPPORTS (timing: Built to Win rolled out summer 2026 → leverage visible from ~1H FY27) | thesis #2 | variance: timing only. The benefit, if any, should land in Q1-Q2 FY27, the quarters where consensus DSG margin is flat (D07-4).

[WA2-5] **Minor and infrastructure items.**
- **(a)** Q1 FY23 10-Q, Item 4: DKS "implemented a new HR management and payroll system". This is the system base for the later "AI in store labor forecasting" (Hobart Q1 FY26). W03 › SRC 10-Q FY2023-Q1. BURIED. conf H on the fact, L on relevance. NEUTRAL.
- **(b)** Q3 FY22 10-Q Ex. 10.7: Separation Agreement with Don Germano, EVP Stores & Supply Chain (2022). Store leadership has turned over since (Ray Sliva now EVP Stores). W03 › SRC 10-Q FY2022-Q3. BURIED. NEUTRAL.
- **(c)** The DKS FLS risk list first adds "labor costs" as a DKS-specific item in the 2025-05-28 Q1 FY25 PR excerpt (425). W08 › SRC 425 2025-05-28_129596. BURIED. Weak AGAINST (labor flagged as a risk before the FY26 step-up).
- **(d)** Grand-opening advertising was reclassified from SG&A into pre-opening from FY24. FY23 pre-opening went from $47.3M to $67.8M recast (+$20.6M), and Q2 FY23 from $22.1M to $32.9M for the 7 HoS conversions. INFERENCE: grand-opening marketing is ≈$1.5-2.3M per HoS-type opening (an upper bound; it includes GGPC and other openings) and is in the one-off pre-opening line. That supports the thesis #2 "one-offs roll off" point only to the extent FY27 openings are fewer. Consensus already has the HoS count at 49 → 68-69, so it is NOT fewer. W03 › 10-Q FY2024-Q1/Q2 recast columns; C01B l.757 | BURIED | conf M | NEUTRAL.

[WA2-6] **Thesis #1 (thin in these files).** The first HoS cohort was mostly in-place conversions of DICK'S/Field & Stream combo stores:
- 7 of the 10 HoS at 7/29/23 were "converted from prior combo store locations".
- 12 Field & Stream stores were closed in Q4 FY22 "for planned near-term conversion to House of Sport, expanded DKS or other specialty". Their square footage stayed in the reported 42.6M (Q1 FY23).
- Q1 FY23 comp was hurt by "lower hunt sales after closing 12 Field & Stream stores".

Read-across (INFERENCE): early HoS comp lift partly reflects the DSG box absorbing the adjacent F&S box's sales. That is a one-time recapture that later relocation-type HoS do not get. Mildly AGAINST using the 2023 cohort's ramp as the template.

| FY22-FY23 | W03 › SRC 10-Q FY2023-Q1/Q2 store-table footnotes | BURIED (partially; H03/H07 mention Baybrook as an F&S conversion) | conf M | AGAINST (mild) | thesis #1 | variance: none.

## Smoking-gun candidates
1. **WA2-1, the 2023 precedent.** "The last time DKS took a severance charge (2023, $26.7M), the personnel line grew just 1.7% the next year. That was $23-34M below the sales-growth path, 0.9-1.3x the severance, inside one year. And management hit its post-action SG&A guide to within 3bp."
   - This is the only hard, dated, company-specific evidence of what a DKS cost action does to the personnel line. Every input is a reported 10-K/10-Q number.
   - Pair it with D07-1/D07-2 (Built to Win plus the +44bp 1H26 deleverage). Applying the 2023 ratio to the ~$21M charge gives ~$18-27M (+$0.15-0.22/sh gross).
   - The honest caveat is part of the exhibit: in 2023 management said savings would be "largely offset by strategic talent investments", and total SG&A ex-charges deleveraged ~50bp in FY24.
2. **WA2-2.** The charge sits in Corporate & other, not segment personnel, so the Q3/Q4 FY26 10-Q personnel line is a clean scorecard. This is a methodological point a PM will remember because it disarms both the bull and the bear misreads.

## Evidence against / caveats
- **Reinvestment risk is documented.** In 2023 DKS said in an 8-K and a 10-Q that savings would be "largely offset by strategic talent investments". FY24 total SG&A ex-charges deleveraged ~+55bp (~+48bp ex deferred comp) while personnel levered 17-25bp. Segment margin rose only because gross margin rose 98bp. Built to Win's release (more Specialists, ">3,200 new leadership opportunities") reads like a reinvestment model, not a cut.
- **The analog differs.** The 2023 cuts were mainly salaried HQ (customer support center) roles plus outdoor/Moosejaw. Built to Win is in the stores, where hourly labor scales with traffic and HoS square footage (~168 staff per HoS, WF). Store labor savings may be smaller per $ of severance.
- **FY24 was a strong year** (comp +5.2%, 53rd-week lap, calendar shifts). Some of the personnel leverage was simply sales leverage. The 52-week adjustment assumes 53rd-week personnel was pro rata (ASSUMPTION).
- **The FY23 wage step never reversed** (WA2-3). Personnel stayed at 13.9-14.0% in FY24-25 despite the 2023 action. The action stopped the growth; it did not reverse the step.
- **The 1H FY26 deleverage is underlying cost, not the charge** (WA2-2). It will not mechanically disappear.
- The W06 bond deal adds ~$66M a year of gross interest (6.2%/6.9% on $1.0B; DUP, known AGAINST, not EPS-neutral). The W08 425s contain no store-labor content.

## Avenue assessment
| Avenue | Access | Signal 1-5 | Script / path |
|---|---|---|---|
| W03 10-Q MD&A (SG&A attributions, guidance trail, business optimization) | open | 4 | scripts\WA2_2023_optimization_analog.py → raw\WA2_2023_analog.csv |
| W03 store tables and footnotes (HoS conversions, F&S exit) | open | 2 | — |
| W06 non-GAAP recon (FY22-FY25 charges, LTM incl. redesign) and capitalization | open | 3 (reconciles corporate & other) | — |
| W08 FL 425 communications | open | 1 (no store-labor or HoS economics content; FLS "labor costs" only) | — |
| SOURCE verification (8-K 2023-08-22, 10-Q FY23 Q2/Q3, 10-K FY23) | open | 5 | — |

## Leads for next wave
- **2023 earnings calls (Q2 FY23 2023-08-22, Q3 FY23 2023-11-21, Q4 FY23 2024-03-07).** These are not in the corpus, which starts at Q3 FY24. Management may have sized the 2023 optimization savings and the "talent reinvestment" there. Try the Seeking Alpha / Motley Fool transcript pages via Bing News RSS, e.g. `https://www.bing.com/news/search?q=%22DICK%27S%22+%22business+optimization%22+2023+savings&format=rss`, or EDGAR full-text search for "business optimization" with DKS 2023-2024 8-K exhibits.
- **The Q3 FY26 10-Q (early Dec 2026) segment note.** Check that "Corporate & other" holds the remaining ~$5.7M of the redesign charge (~$21M FY26 total vs $15.3M in Q2). Then read DICK'S personnel % y/y as the clean Built to Win test (WA2-2). Rerun scripts\D07_dsg_cost_lines.py.
- **Q3 FY26 call question:** "In 2023 you said optimization savings would be largely offset by talent investments. Will Built to Win savings be reinvested, or will they flow through to FY27 SG&A?"
- **10-K FY2026 (Mar 2027):** compare Built to Win's total charge with FY27 personnel growth, using the WA2-1 ratio as the yardstick.
- **WA1 overlap:** reconcile with WA1's headcount series (10-K full-time/part-time counts). Employees per store × personnel per employee would separate wage rate from hours.

## Dead ends / blocked
- No 2023 management transcripts in the corpus, so the 2023 savings were never sized in available material.
- W08 (18 FL 425 filings): no labor or HoS content beyond what is already known. The LinkedIn-post 425s are image-only (no text).
- W06: debt docs carry no store-cost data beyond the non-GAAP recon.

## Duplicates skipped
- Personnel % FY22-FY25 and the quarterly series (KNOWN/D07)
- $15.3M / $21M redesign charge (KNOWN)
- Construction allowances FY22-FY25 and LTM $220.3M (D07-6/F6-5)
- FCF / net capex table (D07)
- Transactions / ticket series (F5-6, primer)
- 53rd week $170.2M / $0.19 (digest)
- ~3/4 of DSG leases renewable within 5 years (F6)
- "90% of stores have premium footwear decks" (digest)
- ~30% of stores in malls (KNOWN)
- $100-125M FL synergies (KNOWN)
- 2025 bonds: $1.0B 6.2% 2036 / 6.9% 2056 and the 4.0% 2029 exchange (digest)
- FY24 HoS/FH conversion split (F2-6)
- 2023-08-22 guide cut / ~$20M severance headline (digest l.118)

STATUS: COMPLETE
