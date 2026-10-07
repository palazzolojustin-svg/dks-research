# WA6 (wave 2): W21 peer consensus/financials + W04 DKS 10-Qs Q1 FY25 to Q2 FY26 (thesis #2 lines)
Agent WA6 | 2026-10-07

**Files read in full:** WORKING_NOTES\W04_DKS_10Q_FY25Q1-FY26Q2.md (lines 1-1218) and WORKING_NOTES\W21_PEER_CONSENSUS_FINANCIALS_AND_PEER_MARKET_DATA.md (lines 1-2556).

**Verified in SOURCE:** the 10-Q segment-note footnote defining personnel, and the incentive-comp, healthcare and SG&A-driver sentences:
- DKS_10-Q_FY2025-Q1 l.643, l.968
- DKS_10-Q_FY2025-Q3 l.997, l.1432, l.1467, l.1533, l.1591
- DKS_10-Q_FY2026-Q2 l.887, l.1075, l.1285, l.1320, l.1395, l.1453, l.1550
- DKS_10-Q_FY2024-Q1/Q2/Q3 incentive-comp lines (l.893; l.955, l.981; l.959, l.985)

**Script:** THESIS_SCRAPE\scripts\WA6_dsg_cost_split.py writes THESIS_SCRAPE\raw\WA6_dsg_cost_split.csv.

**Novelty checks** (Grep of digest, primers, KNOWN_BRIEF, wave1 and wave2):
- "administrative employees", "admin wages", "store & admin": 0 hits
- "incentive": only D07/KNOWN_BRIEF ("rebuild in FY27") and the WA2 FY22/FY24 mentions
- "shipping"/"Fort Worth": the primers know both as GM headwinds, but neither is sized from the segment table
- "13.67" (short interest) and "-10.4" (Nike North America wholesale): already in the primer, so DUP

**Overlap read first:**
- D07 and F6 (the quarterly personnel series, DUP).
- WA2: the redesign charge sits in Corporate & other, ~$5.7M of the charge remains, and the 2023 analog. All DUP, not re-reported.

**Variance constants:** FY27E DICK'S segment revenue $15,203M; 10bp = $15.2M = $0.124/sh; $1M pre-tax = $0.00814/sh.

## Top findings (ranked)

[WA6-1] **The full split of the 1H FY26 DICK'S segment-margin decline (−54bp). It shows that half of D07's "other expense +60bp" is logistics cost booked in COGS plus pre-opening, not SG&A. Personnel is the only large SG&A line that deleveraged in both quarters.**

Method: the CODM "other segment expenses" line mixes GAAP COGS items with SG&A items. The Q3 FY25 10-Q note says DICK'S supply chain and shipping sit in "other" for the DICK'S segment, but in cost of goods for Foot Locker. I split "other" three ways:
- COGS-side "other" = (segment sales − DICK'S gross profit) − cost of merchandise & services − occupancy. This captures shipping, e-commerce fulfilment and DC/supply-chain cost, including the Fort Worth DC.
- Pre-opening.
- SG&A-side "other" = advertising, bank card, technology, e-com platform, other store, Customer Support Center non-wage.

The split reconciles to management's own bridges:
- Q2 FY26 DICK'S SG&A deleverage of 96bp = personnel +43 + SG&A-other +53.
- Q1 FY26 SG&A deleverage of 31bp = +45 − 14.
- Q3 FY25 SG&A deleverage of 45bp = +6 + 40.
- Q2 FY24 GAAP SG&A reconciles to the dollar.

| bp of DICK'S sales, y/y | Q1FY25 | Q2FY25 | Q3FY25 | Q4FY25 | Q1FY26 | Q2FY26 | **1H FY26** |
|---|---|---|---|---|---|---|---|
| Merch & services cost | −37 | −18 | −5 | −73 | +29 | −137 | **−59** |
| Occupancy | +6 | −8 | −10 | +11 | −2 | +19 | **+10** |
| COGS-side other (shipping, fuel, DC) | −10 | −7 | −13 | −6 | +8 | **+39** | **+25** |
| Pre-opening | −28 | +8 | +37 | +1 | −1 | +25 | **+13** |
| SG&A-side other (marketing, tech, card, CSC) | +61 | +56 | +40 | −50 | −14 | +53 | **+22** |
| Personnel | −31 | +20 | +6 | +27 | **+45** | **+43** | **+44** |
| Segment margin | +39 | −51 | −56 | +88 | −66 | −42 | **−54** |

Q1-Q2 FY25 use the recast "other" from the FY26 10-Qs. Q4 = FY − 39 weeks.

What this means for thesis #2:
- (a) The logistics piece (+25bp) is a gross-margin item. Consensus FY27 DICK'S GM is only +7bp, so its lap belongs in the GM debate (D02's turf), not in "SG&A leverage".
- (b) The SG&A-side "other" line deleveraged hard all through FY25 (+61/+56/+40bp in Q1-Q3; tech & talent, marketing). It levered in Q4 FY25 and Q1 FY26, then deleveraged again in Q2 FY26 (World Cup).
- (c) Personnel is the one SG&A line that deleveraged in both FY26 quarters: +45 and +43bp, or 60% of DICK'S 1H SG&A $ growth (+$88.0M of +$146.2M). In Q1 it was 72% (+$44.2M of +$61.0M).

| Q1 FY24 to Q2 FY26 | W04 › 10-Q segment notes (Note 7/9) and segment MD&A GP; W01 › 10-K FY25 segment table, pre-opening; SOURCE 10-Q FY2026-Q2 l.1395 | accessed 2026-10-07 | method: python, scripts\WA6_dsg_cost_split.py | NEW calc (D07/F6 only had the four CODM lines; the COGS/SG&A split of "other" exists in no wave or digest file) | conf H for Q1 FY25 to Q2 FY26 (DSG pre-opening uses management-rounded $ increments, ±$0.05M); M for FY24 Q1-Q2 (not recast) | NEUTRAL (sharpens the thesis) | thesis #2 | variance: it reframes the target. The addressable SG&A deleverage in 1H FY26 is personnel +44bp plus SG&A-other +22bp. The +25bp logistics and the +13bp pre-opening sit outside "store-cost reset" leverage.

[WA6-2] **Correction to D07-4: the Q2 FY26 "$34M World Cup other-expense excess" is really ~$15M of logistics cost in gross margin plus ~$20M of SG&A excess. The ~$20M is the same size as the SG&A-other excess in Q1 and Q2 FY25, when there was no World Cup.**

"Excess" means $ above what the line would have been had it grown with DICK'S sales (+5.57% in Q2 FY26):

| Excess vs sales-growth path ($M) | Q1FY25 | Q2FY25 | Q3FY25 | Q4FY25 | Q1FY26 | Q2FY26 |
|---|---|---|---|---|---|---|
| COGS-side other | −3.1 | −2.5 | −4.1 | −2.5 | +2.9 | **+14.9** |
| SG&A-side other | +19.3 | +20.3 | +12.9 | −20.1 | −4.6 | **+20.4** |
| Personnel | −9.9 | +7.4 | +1.8 | +11.1 | +15.2 | **+16.6** |

- SG&A-side other y/y growth: +11.6%, +10.9%, +9.8%, −0.5%, +5.0%, **+11.0%**.
- Two readings of the World Cup one-off (INFERENCE):
  - Against the recent run-rate (Q4 FY25 to Q1 FY26 at −0.5% to +5%), Q2's +11% implies a **~$20-23M** World Cup and marketing bump.
  - Against the FY25 run-rate (+10-12%), there is no anomaly at all.
- Honest range for the SG&A-side roll-off in Q2 FY27: **$0-23M, central ~$15-20M ≈ 10-13bp of FY27 DICK'S sales ≈ +$0.12-0.16/sh**. D07 had $15-30M; this narrows it.
- The +$14.9M COGS-side excess is a GM item. MD&A attributes it to "higher shipping (higher eCom sales, elevated fuel) and supply chain incl first full quarter of Fort Worth TX DC".

| Q1 FY25 to Q2 FY26 | as WA6-1; SOURCE 10-Q FY2026-Q2 l.1395 (DICK'S SG&A drivers); W04 l.1190 (GP drivers) | 2026-10-07 | python | NEW calc (extends D07-4) | conf M-H | AGAINST, mildly: the World Cup roll-off is smaller and less certain than D07 sized | thesis #2 (one-offs roll off) | variance: −$0.0 to −$0.10/sh vs D07-4's midpoint.

[WA6-3] **Calibration of D02's fuel model against reported data. Q2 FY26 logistics cost rose +39bp y/y; D02's fuel model explains ~22bp, leaving ~17bp (~$6.5M) for the Fort Worth DC start-up and e-com mix. In Q1 the residual was −8bp.**
- COGS-side other was +8bp y/y in Q1 FY26 and +39bp in Q2 FY26. D02-1's fuel estimate is −16bp (Q1) and −22bp (Q2).
- The residual is ≈ −8bp in Q1 (MD&A: "partly offset by supply chain leverage") and ≈ **+17bp ≈ $6.5M in Q2**, the "first full quarter of Fort Worth TX DC".
- So the DC start-up drag is roughly $6-7M in its first full quarter. That is consistent with D02-8's +10-15bp lap in Q1-Q2 FY27.
- FY25 had leverage of −6 to −13bp every quarter on this line ("lower eCom shipping & fulfillment"). The FY26 swing is therefore a reversal, not a trend.

| Q1-Q2 FY26 | as WA6-1 + THESIS_SCRAPE\wave1\D02.md (D02-1, D02-8) | 2026-10-07 | arithmetic | NEW calc | conf M (the residual inherits D02's fuel assumptions) | SUPPORTS, slightly (the DC drag is bounded and laps) | thesis #2 (FY26 one-offs) | variance: if the DC residual normalizes, ~+$6-7M in Q2 FY27 and perhaps ~$10-15M FY27 ≈ +7-10bp of GM ≈ +$0.08-0.12/sh, a GM-line item. Partly offset by D02's 1H FY27 fuel headwind.

[WA6-4] **The bonus cycle muddies the "clean Q3 FY26 test" and weakens the "return to FY25's 13.98%" bull case.** In every filing MD&A names incentive comp as an SG&A driver:
- **FY24: "higher incentive compensation"** in Q1 (SOURCE 10-Q FY24Q1 l.893), Q2 (l.955) and Q3 (l.959).
- **FY25: "lower incentive compensation"** in Q1 (10-Q FY25Q1 l.968: "partially offset by lower incentive compensation compared to the quarter ended May 4, 2024"), Q3 (10-Q FY25Q3 l.1432, l.1533), 39 weeks (l.1467, l.1591) and the full year (10-K FY25 MD&A, W01 l.254, l.274).
- **FY26 1H: no incentive-comp mention** among the SG&A drivers. The cash-flow text cites "year-over-year changes in incentive compensation accruals and corresponding payments" (Q1 l.1437; Q2 l.1550), meaning the smaller FY25 bonus was paid in Q1 FY26.

Implications (INFERENCE):
- (a) **FY25's 13.98% personnel ratio was flattered by a below-plan bonus year.** Returning to 13.98% in FY27 would need bonus at FY25's depressed level as well as Built to Win savings. D07's +$0.52 "return to 13.98%" bull case is therefore partly a bonus effect.
- (b) The August 2026 guide cut took DICK'S segment profit to $1.54-1.60B from $1.60-1.68B. 2H FY26 accruals were probably trued down, which **lowers Q3/Q4 FY26 personnel for reasons unrelated to Built to Win**.
  - The Q3 10-Q "test" proposed by D07 and WA2 can therefore flatter.
  - The real read is FY27 against a re-based bonus.
- (c) FY27 consensus (+29bp DICK'S margin) has to absorb a bonus rebuild after a missed FY26.
- (d) Even so, management did NOT cite incentive comp for the 1H FY26 personnel step-up. It cited "technology and talent", store-model redesign costs (excluded from the segment) and "higher teammate healthcare costs". So the +44bp is not a bonus artefact.

| FY24-FY26 | SOURCE 10-Q FY24Q1-Q3, FY25Q1/Q3, FY26Q1/Q2 (lines above); W01 › 10-K FY25 MD&A | accessed 2026-10-07 | read + verify | BURIED (digest/primers have no incentive-comp language; KNOWN_BRIEF only says "rebuild in FY27"; WA2 cites FY22/FY24 only) | conf H (facts), M (implications) | AGAINST (FY27 rebuild; cleanliness of the test) / SUPPORTS (d) | thesis #2 | variance: not sizable from filings. Every 10% of a bonus pool that is perhaps 1-2% of personnel is ~$2-4M ≈ 1-3bp ≈ $0.02-0.03/sh (INFERENCE, low confidence).

[WA6-5] **"Personnel" is not only store labor. The 10-Q defines it as "wages, salaries, and other forms of compensation related to store and administrative employees". The 10-K SG&A definition adds "store/field/admin/GameChanger payroll".**
- Management's SG&A driver every quarter since Q1 FY25 is "strategic digital and in-store investments across technology and talent".
- So part of the +44bp is headquarters tech and digital talent, field management and GameChanger engineers. Built to Win does not touch these.
- The store share of the ~$2.0B FY25 personnel pool is not disclosed.
- Healthcare is self-insured with stop-loss (W01 l.463), so "higher teammate healthcare costs" are claims-driven and sit inside "other forms of compensation".

| FY25-FY26 | SOURCE 10-Q FY2025-Q1 l.643 (footnote 2; same text in FY25Q2 l.686, FY25Q3 l.997, FY26Q1 l.865, FY26Q2 l.887); W01 l.246 (10-K SG&A definition), l.463 | 2026-10-07 | read | BURIED (0 hits for "administrative employees"/"admin wages" in digest, primers or wave files) | conf H | AGAINST, mildly (the addressable store pool is smaller than headline personnel; part of the deleverage is HQ/GameChanger investment the redesign won't reverse) | thesis #2 | variance: it scales down D07's gross +$0.52. If, say, 15-25% of the 1H FY26 personnel growth was non-store (unknown; INFERENCE), the store-addressable deleverage is ~33-37bp, not 44bp.

[WA6-6] **Labor-intensity series: in FY26 the extra personnel cost is per box, not from more stores.** The DICK'S Business store count was flat (888 to 892) and square footage rose ~2%. Yet:

| y/y | Q1 FY26 | Q2 FY26 |
|---|---|---|
| Personnel $ per average store | **+9.3%** | **+8.6%** |
| Personnel $ per average sq ft | **+8.2%** | **+7.2%** |
| Sales per sq ft | +4.9% | +3.8% |

- Personnel ran above a sales-proportional path by **−$9.9M, +$7.4M, +$1.8M, +$11.1M, +$15.2M and +$16.6M** (Q1 FY25 to Q2 FY26). That is accelerating, and totals **+$44.7M over the last four quarters**, ≈ 29bp of FY27E DICK'S revenue ≈ $0.36/sh.
- With retail wage growth at ~3-4% (D02-5), roughly **4-5pts of the ~8% per-sq-ft growth is hours, headcount or mix** (HoS staffing, Specialists/leads, healthcare, HQ talent). That is the pool Built to Win and AI scheduling can act on (INFERENCE).

| Q1 FY25 to Q2 FY26 | W04 store tables (end-of-quarter counts and sq ft; the sq ft basis changed to "gross" at Q3 FY25 with an unchanged beginning figure, so the effect is ~±1%) + segment notes | 2026-10-07 | python | NEW calc | conf M | SUPPORTS (sizes an addressable pool) / AGAINST (shows it is growing) | thesis #2 | variance: if FY27 personnel merely grows at sales growth, the LTM ~$45M excess stops compounding. Consensus already has ~+22bp of SG&A leverage, so the net variance vs consensus is ~0 to +$0.15 unless hours actually fall (consistent with D07 and WA2).

[WA6-7] **W21 (peer consensus) has no store-labor read-across.** W21 holds Bloomberg consensus only for brands (DECK, NKE, ONON) plus price and valuation panels; there is no retailer SG&A consensus and no ASO. Brand consensus SG&A paths for the next fiscal year:
- DECK: SG&A 34.63% (FY26A) → 35.20% (FY27E), +57bp of deleverage.
- NKE: selling & administrative 34.73% → 35.53% (FY27E), +80bp, on revenue −6.1%.
- ONON: opex 51.62% (2026E) → 51.12% (2027E), −50bp of leverage on +18.9% constant-currency growth.

By contrast, DKS consensus has ~+22bp of DICK'S SG&A leverage on ~+3% sales growth. That leverage is more demanding than for brands with similar growth. It is not comparable, though, because the brands' SG&A is demand creation, not store labor.

| FY26-FY27E | W21 › SRC 06_BLOOMBERG_FINANCIALS/DECK, NKE (TRANSCRIBED), ONON annuals | 2026-10-07 | read | BURIED (not cited anywhere) | conf H for the data, L for relevance | NEUTRAL | thesis #2 | variance: none.

## Smoking-gun candidates
1. **WA6-1 + WA6-6 together (the cleanest exhibit for the deck).**
   - Of the 54bp decline in DICK'S 1H FY26 margin, personnel is 44bp. It is the only SG&A line that deleveraged in both quarters. It is growing ~8% per square foot and ~9% per store while the store count is flat.
   - Logistics (+25bp) and pre-opening (+13bp) are separate and largely timing-driven.
   - A PM will remember "the margin problem is labor per box, and that is exactly what DKS restructured in summer 2026".
   - It is a reframing built from reported numbers, not proof of savings.
2. **WA6-4 (the bonus cycle)** is the "gotcha" the pitch must pre-empt.
   - A good Q3 FY26 personnel print may simply be a bonus true-down after the August cut.
   - FY25's 13.98% was a low-bonus year.
   - Owning this caveat makes the thesis more credible. Measure Built to Win on FY27 personnel $ per store, not on the Q3 ratio.

## Evidence against / caveats
- The World Cup roll-off is smaller and less certain than D07-4 claimed (~$15-20M SG&A-side, not $34M; WA6-2). About $15M of the Q2 "excess" is fuel, shipping and DC cost in gross margin, and fuel stays a headwind in 1H FY27 (D02-1).
- Personnel includes headquarters/admin, field and GameChanger payroll (WA6-5). The store-addressable share of the deleverage is smaller than 44bp.
- The bonus cycle (WA6-4): FY25 was a low-bonus base, and FY27 rebuilds after the FY26 miss. A Q3/Q4 FY26 improvement may be bonus, not redesign savings.
- Labor intensity per box is rising ~4-5pts a year above wage inflation (WA6-6). Part of this is structural (HoS staffing, Specialists, healthcare is self-insured and trending +8.2% in 2027 per D02-6).
- SG&A-side "other" (tech, marketing) grew ~10-12% y/y through most of FY25 (WA6-2). DKS has a habit of reinvesting (consistent with the 2023 "largely offset by talent investments" language in WA2-1).
- W21 offers no retailer peer evidence that store-labor leverage is being modelled anywhere (WA6-7).

## Avenue assessment
| Avenue | Access | Signal 1-5 | Script / path |
|---|---|---|---|
| W04 segment notes + segment MD&A GP → split "other" into COGS-side, pre-opening and SG&A-side | open | 5 | scripts\WA6_dsg_cost_split.py → raw\WA6_dsg_cost_split.csv |
| W04/SOURCE MD&A SG&A-driver language (incentive comp, healthcare, tech & talent) FY24-FY26 | open | 4 | SOURCE 10-Q lines cited |
| 10-Q/10-K personnel definition | open | 4 | SOURCE 10-Q footnote (2) |
| W04 store tables → personnel per store and per sq ft | open | 3 | same script |
| W04 FL segment, PPA, debt, legal | open | 1 for thesis #2 (excluded or known) | — |
| W21 Bloomberg consensus (DECK/NKE/ONON), peer price panel, valuation snapshot | open | 1 (brands only; no store-labor content; Nike NA wholesale −10.4% and the DKS short-interest figure are already in the primer) | — |

## Leads for next wave
- **Q3 FY26 10-Q (early Dec 2026):** rerun scripts\WA6_dsg_cost_split.py with the Q3 row. Watch personnel $ per store y/y (Q1 +9.3%, Q2 +8.6%) rather than the ratio, because of the bonus true-down (WA6-4). Read the MD&A for "lower incentive compensation" in Q3 FY26: if it appears, part of any improvement is bonus.
- **Q3 call question:** "How much of 2026 personnel growth was store vs CSC/GameChanger talent, and what is the run-rate store-hours change since Built to Win went live?"
- **10-K FY26 (Mar 2027):** the human-capital section (full-time/part-time counts; WA1) combined with personnel $ gives cost per employee vs headcount. That separates rate from hours, which the 10-Qs cannot.
- **L5:** use WA6_dsg_cost_split.csv as the base. The COGS-side logistics line belongs in the GM model, not SG&A, and only SG&A-side other plus personnel should feed the "store-cost reset".

## Dead ends / blocked
- No quarterly split of store vs administrative personnel exists in any filing. No disclosed bonus-pool size (the 10-Q accrued-expense detail is not broken out in W04).
- W21 contains no retailer (ASO, BBY, ULTA) consensus SG&A or labor data, only price and valuation snapshots for those names.
- SBC allocation unknown: whether DICK'S personnel ("other forms of compensation") includes SBC is not stated. 1H FY26 consolidated SBC was $53.9M vs $37.9M, partly FL replacement awards. If SBC is inside, part of the +44bp could be equity comp; unresolved.

## Duplicates skipped
- Personnel % quarterly and annual series, and the +44bp (D07/F6/KNOWN_BRIEF).
- $15.3M / ~$21M redesign charge; the charge sitting in Corporate & other and ~$5.7M remaining (WA2-2).
- 2023 business optimization analog (WA2).
- Construction allowances (D07-6/F6-5); OBBBA cash-tax deferral (F6-11).
- Fort Worth DC and fuel as GM headwinds (primer, D02).
- Nike NA wholesale cc −10.4% Sep-Nov 2026 and the DKS short interest of 13.67% (primer).
- Healthcare +8.2% 2027 trend (D02-6).
- FL org-alignment charges $50-55M and FL synergies (known; FL topics excluded).
- DSG store counts and sq ft (KNOWN_BRIEF).

STATUS: COMPLETE
