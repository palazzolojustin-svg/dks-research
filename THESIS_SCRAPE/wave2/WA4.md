# WA4 (wave 2): sweep of W05_DKS_8K_PRESSRELEASES_C.md + W20_SECTOR_MACRO.md, then the adjacent wage-floor avenue
Agent WA4 | 2026-10-07 | Files read IN FULL: WORKING_NOTES\W05_DKS_8K_PRESSRELEASES_C.md (l.1-1437; 23 SRC: 8-K covers + Ex 99.1 releases Q2FY25-Q2FY26, FL deal/pro-forma 8-Ks, annual-meeting 8-K, notes 8-Ks) and WORKING_NOTES\W20_SECTOR_MACRO.md (l.1-364; 16 SRC: Needham, BI, Barclays, DB, Williams, JPM Euro sporting goods, BI credit).
Novelty checked by Grep against CORE_NOTES\00_CORE_DIGEST.md, FL_EUROPE_SCRAPE\baseline\primers\PRIMER_DENSE/READABLE.html, KNOWN_BRIEF.md and THESIS_SCRAPE\wave*\*.md.
Variance constants: FY27E DSG revenue $15,203M, OI $1,647M (10.83%); 89.09M shares; 27.46% tax; $1M pre-tax = $0.00814/sh; 10bp of DSG margin = $15.2M = $0.124/sh.

**Bottom line.** Both assigned files are thin on store labor:
- W05C has no personnel line. The 8-K releases give segment profit, store tables, capex/allowances and guidance reconciliations. The personnel detail is in the 10-Qs, already mined by D07/F6.
- W20 has no DKS labor data, only macro labor-market colour.

I therefore (a) built the one fresh calculation the files support that bears directly on thesis #2's timing (a half-year decomposition of consensus), and (b) pivoted to the closest adjacent avenue that produces wage-rate evidence: the statutory minimum-wage path weighted by DKS's actual store footprint, including a NEW datapoint (New York's 2027 minimum-wage freeze).

Scripts:
- scripts\WA4_consensus_halves.py → raw\WA4_consensus_halves.csv
- scripts\WA4_minwage.py → raw\WA4_minwage_by_state.csv, raw\WA4_minwage_weighted.csv, raw\WA4_dol_state_*.html, raw\WA4_dol_rates_parsed.json
- scripts\WA4_news_rss.py and scripts\WA4_bing.py → raw\WA4_news_rss.json, raw\WA4_bing.json

## Top findings (ranked)

[WA4-1] **Consensus has the DICK'S-segment margin DOWN y/y in 1H FY27, the first full half under the new store model. All of the consensus FY27 margin expansion sits in 2H FY27.**

Half-year DSG segment margins:
| Period | Revenue $M | OI $M | Margin | Basis |
|---|---|---|---|---|
| 1H FY25 | 6,821.3 | 835.4 | 12.25% | actual |
| 2H FY25 | 7,287.6 | 733.1 | 10.06% | actual |
| 1H FY26 | 7,227.3 | 846.2 | 11.71% | actual |
| 2H FY26E | 7,581.0 | 703.6 | 9.28% | consensus |
| **1H FY27E** | 7,580.7 | 852.6 | **11.25%** | consensus |
| 2H FY27E | 7,622.3 | 794.5 | 10.42% | consensus, derived: FY27E 1,647.2 − 1H27E |
| FY27E | 15,203 | 1,647 | 10.83% | consensus |
| FY25 | 14,108.9 | 1,568.4 | 11.12% | actual |

- **1H FY27E is −46bp y/y on the OI/revenue rows.** On BBG's separately averaged margin rows (Q1 10.07%, Q2 11.69%) it is 10.95%, or −76bp.
- Q1 FY27E is −5bp (OI/rev) or −62bp (margin row). Q2 FY27E is −84bp or −91bp.
- **2H FY27E is +114bp** vs consensus 2H FY26E: it laps the guided trough.
- So consensus credits NO labor-model savings in 1H FY27, even though:
  - "Built to Win" was rolled out in summer 2026;
  - ~73% of the FY26 redesign charge ($15.3M of ~$21M) was already booked in Q2 FY26, which implies the rollout was largely done by 8/1/26 (INFERENCE);
  - 1H FY27 laps the ~$34M Q2 FY26 World Cup marketing excess (D07-4, ≈ +45bp of 1H sales) against the ~$19-21M current-year tariff refund in Q2 FY26 DSG GM (≈ −25-28bp).
- Net of those two one-offs, consensus implies **underlying 1H FY27 deleverage of roughly −63 to −93bp**. 1H FY26 was −54bp, of which personnel was +44bp.
- Caveat: the GM-vs-opex split is NOT robust. BBG's segment GP row and GM% row come from different contributor sets: the GP row implies 1H27E GM −88bp with opex leverage +42bp, while the GM%/OM% rows imply GM −20bp with opex deleverage −56bp. Only the sign of the OI margin (down) holds on every row.

| 1H FY25-2H FY27E | Actuals: W05C › SRC 8-K Ex 99.1 2025-08-28 / 2025-11-25 / 2026-03-12 / 2026-05-27 / 2026-08-25 (segment tables). Consensus: CORE_NOTES\C05 l.214-218 + digest §7a/7b | accessed 2026-10-07 | method: python, scripts\WA4_consensus_halves.py | NEW (fresh calc; the quarterly consensus is DUP but the 1H27/2H27 split and the "no savings in 1H27" reading appear nowhere in the digest, primers or wave files) | conf M (the arithmetic is H; BBG segment rows have thin and uneven contributors) | SUPPORTS | thesis #2 (timing / where the variance sits)

Variance (INFERENCE): if Built to Win merely holds 1H FY27 DSG margin flat y/y at 11.71%:
- vs consensus 11.25%: +46bp × $7,581M = **+$35M pre-tax ≈ +$0.28/sh**;
- vs the margin-row 10.95%: +76bp ≈ +$58M ≈ **+$0.47/sh**.

That is the 1H-only upside before any 2H FY27 effect. The test comes in stages:
- the Q3 FY26 10-Q personnel line (~early Dec 2026);
- the Q4 FY26 SG&A, which management guided to lever (digest §3).

[WA4-2] **New York, DKS's 4th-largest store state (49 DICK'S Business stores, 5.5% of the 888 US fleet), will NOT raise its minimum wage on 2027-01-01.**
- The 2023 law's off-ramp was triggered by state private-sector job losses.
- Rates stay $17.00 (NYC/LI/Westchester) and $16.00 (rest of state), after +$0.50 in each of 2024, 2025 and 2026.
- Gov. Hochul is pitching a legislative "fix" (Times Union 2026-09-30), so the freeze could be reversed.

| Jan-2027 | Newsday "Long Island's minimum wage will stay frozen at $17 because of job losses" (2026-10-01); Syracuse.com (2026-10-01); MSN/BI-syndicated "New York forced to skip planned minimum wage increase…" (2026-10-06); Times Union (2026-09-30); Observer Today "Jobs decline prompts freeze in state minimum wage" (2026-10-06). All found via Google News / Bing News RSS (raw\WA4_news_rss.json, raw\WA4_bing.json) | accessed 2026-10-07 | method: news RSS titles and descriptions (article bodies not fetched: MSN is JS-rendered, Google links redirect) | NEW | conf H (five independent outlets) | SUPPORTS (mild) | thesis #2 (wage rate) | variance: see WA4-3. It is also a datapoint that the labor market in a core DKS state is loosening, which supports D02-5's AHE slowdown.

[WA4-3] **The DKS-footprint-weighted statutory wage floor decelerates into FY27, but three big-footprint states take +7-9% steps.**

Floors weighted by DKS's 888 US DICK'S Business stores (10-K FY25 Item 2 store-by-state table; effective floor = max(state rate, $7.25); NY blended 50/50 upstate/downstate):

| Jan-1 | DKS-weighted avg floor | y/y | Share of DKS stores getting an increase | y/y in states with a floor ≥ $12 |
|---|---|---|---|---|
| 2024 | $11.01 | — | — | — |
| 2025 | $11.39 | +3.4% | 53.4% | +4.4% (425 stores) |
| 2026 | $11.67 | +2.5% | 47.9% | +3.7% (457 stores) |
| **2027** | **$11.94** | **+2.3%** | **39.3%** | **+3.2%** (457 stores) |

- ~40% of DKS stores (354) sit in $7.25 states (PA 51, TX 63, NC 42, GA 26, IN 25, TN 20 and others), where the statutory floor does not bind.
- Jan-2027 announced or scheduled rates:
  - CA $16.90 → $17.40 (+3.0%)
  - WA $17.13 → $17.73
  - NJ $15.92 → $16.48
  - OH $11.00 → $11.40 (+3.5%)
  - CO $15.16 → $15.71
  - CT $16.94 → $17.48
  - AZ $15.15 → $15.65
  - MN $11.41 → $11.87
  - ME $15.10 → $15.70
  - RI $16 → $17
  - IL, MD, MA, MO stay flat at $15
- **AGAINST, big steps:**
  - FL (59 stores): $14 → $15 on 2026-09-30 (final step of Amendment 2; CPI-indexed thereafter).
  - MI (26 stores): $13.73 → $15.00 on 2027-01-01, after $10.56 → $12.48 (2/2025) → $13.73 (1/2026).
  - VA (32 stores): $12.77 → **$13.75** (+7.7%) on 2027-01-01 (doli.virginia.gov homepage).
  - Together these are 117 stores (13% of the fleet) moving to a ~$14-15 floor, which can compress entry pay where DKS hourly rates sit near $15.

| Jan-2024 to Jan-2027 | DOL WHD "State Minimum Wage Laws" (https://www.dol.gov/agencies/whd/minimum-wage/state, "Updated July 1, 2026") + Wayback snapshots 20240301011506 / 20250303090553; 2027 rates per state from official pages or press (list in scripts\WA4_minwage.py SRC27); store counts from SOURCE\01_DKS_SEC_FILINGS\10-K\DKS_10-K_FY2025_filed-2026-03-27.md l.1052-1080 | accessed 2026-10-07 | method: python, scripts\WA4_minwage.py | NEW (no minimum-wage data anywhere in the corpus or wave files) | conf M. Caveats: local minimums are ignored (Seattle $22.14, Denver, Twin Cities > $17, Omaha); NE 2027 = $15.26 is INFERENCE; VT/SD/MT indexation is assumed (3 stores); OR/DC/AK July-indexed rates are carried flat | NEUTRAL-to-mild SUPPORT | thesis #2 (wage-rate input)

Variance (INFERENCE): this is small on its own.
- If wage-rate growth in floor-binding states slows ~0.5pt (3.7% → 3.2%) on ~half of ~$2.1B FY27E store personnel: ≈ $5M ≈ 3bp ≈ **+$0.04/sh**.
- The FL/MI/VA steps could absorb that, so the net is ~0.
- Its use in the pitch is to rebut "wage inflation is re-accelerating". Mandated floors across DKS's footprint grow ~2.3% in 2027 (the slowest of the four years), consistent with D02's retail AHE slowdown to ~3%.

[WA4-4] **Landlord allowances in 1H FY26 are 99.8% DICK'S, not Foot Locker. This resolves the F6-5 caveat that FL Fast Break remodels might be inflating the surge.**
- 8-K segment capex tables, landlord construction allowances:
  - Q1 FY26: DICK'S $70.548M vs FL $1.175M.
  - 26 weeks FY26: DICK'S **$128.962M** vs FL **$0.301M**. Consolidated 1H FY25 was $70.583M (all DICK'S).
- DICK'S allowances as a share of DICK'S gross capex:
  - Q1 FY26: 23.9% (70.5/294.9) vs Q1 FY25 8.6% (22.8/264.7);
  - 1H FY26: **21.4%** (129.0/603.2) vs 1H FY25 13.4% (70.6/526.1).
- DICK'S net capex: 1H FY26 $474.3M vs 1H FY25 $455.5M (+4%), while gross capex rose +15%.

| Q1 FY25-1H FY26 | W05C › SRC 8-K/exhibits/DKS_8-K_2026-05-27_EX-99-1 (net capex table) and DKS_8-K_2026-08-25_EX-99-1 (net capex table) | accessed 2026-10-07 | method: read + ratio | BURIED (split never surfaced; D07-6/F6-5 had the totals and flagged the FL contamination risk) | conf H | SUPPORTS | thesis #1 (landlords fund the format build; returns) | variance: FCF/returns only, no EPS.

[WA4-5] **The FY26 redesign charge was not in the May guidance; it appeared only in August, and ~73% was booked in one quarter.** Timing detail from the guidance reconciliations:
- The 2026-05-27 Q1 reconciliation (six weeks after the 2026-04-14 Built to Win release) has only two items: FL costs +$200M and settlements −$174M. There is no store-model line.
- The 2026-08-25 reconciliation adds "+ store operating model redesign 21 (EPS 0.17)", and Q2 booked $15.349M (non-GAAP SG&A add-back, "severance, training and other costs").
- That leaves ~$5.7M for 2H FY26. The charge sits in "Corporate & other", so DSG segment profit and its consensus are clean of it and any savings flow straight to the DSG line.
- In May, management still raised the DSG margin guide to 11.0-11.4% and said DSG SG&A would lever in 2H (digest §3).

| Apr-Aug 2026 | W05C › SRC DKS_8-K_2026-05-27_EX-99-1 (guidance reconciliation) vs DKS_8-K_2026-08-25_EX-99-1 (reconciliation and footnote 3; segment note (2)) | accessed 2026-10-07 | method: read + arithmetic | BURIED (the $21M/$15.3M figures are DUP; the May-vs-Aug absence and the ~73%-booked-in-Q2 timing are new framing) | conf H on facts, M on the "rollout complete by Q2" inference | SUPPORTS | thesis #2 (timing: Q3 FY26 is the first clean quarter) | variance: none by itself; it dates when savings should start to show.

[WA4-6] **Sector/macro labor colour in W20 (BURIED, weak, mixed).**
- BI credit (2026-07-29): "HY retail bonds may widen as tariff & labor risks challenge cash-flow recovery". It also charts "Drewry container rate, Atlanta Fed wage growth", but the values were not extracted.
- DB channel checks (2026-07-22, US retailer #1): with promotions capped, retailers instead "reduced vendor marketing support, modest expense controls". Peers were trimming costs in mid-2026.
- BI credit weekly (2026-10-02): forecasts of "about 90,000 September payroll gains" and talk of "More Federal Reserve rate hikes". That points to a cooling labor market with sticky inflation.
- Against that, JPM (2026-07-02) cites a "re-accelerating labour market".

| W20 › SRC 05_SECTOR_MACRO/2026-07-29_BloombergIntel_..._Chart_Pack; 2026-07-29_DeutscheBank_AS_..._Chan; credit/2026-10-02_BloombergIntel_..._Credit_Best; SECTOR_MACRO_and_ADIDAS_PUMA_Summaries (JPM D1) | BURIED | conf L | NEUTRAL | thesis #2 context only.

### Duplicates skipped (one line each)
- FY26 DSG guide path (11.0-11.2% → 11.0-11.4% → 10.6-10.9%) and the 2H implied 9.5-10.1%: digest §3, PRIMER_DENSE.
- Consensus FY26E DSG margin below the guide only because of the revenue denominator: PRIMER_DENSE l.477.
- Q3 FY26E DSG 7.17% (−175bp): digest §7b, primer.
- Consensus pre-opening FY26E $87.1M / FY27E ~$86.9M (no roll-off): F4.
- Q2 FY27E DSG OI ≈ flat vs Q2 FY26: D07-4.
- Store tables (HoS 3 new + 13 relocations FY25; 0 new + 6 relocations 1H26): F6-8/digest.
- Construction-allowance totals: D07-6/F6-5.
- FY25 DSG SG&A +41bp deleverage: primer.
- $15.3M/$21M redesign charge: KNOWN_BRIEF.
- "teammate organizing efforts" risk factor: boilerplate in the 10-K since FY23 (DKS_10-K_FY2023 l.590-594); only added to the press-release FLS list in Mar-2026. No finding.
- Stack's ">100,000 teammates across the globe" (2026-03-12 release): headcount is WA1's 10-K territory.
- FLS additions in Aug-2026 ("AI and machine learning", "distribution/fulfillment network optimization"): too thin to be a finding.
- W20 brand and channel content (Nike/On/adidas order books, promotions, FL promo screens): not thesis #1/#2.

## Smoking-gun candidates
1. **WA4-1: "The Street has DICK'S margin falling again in 1H FY27, the first full half of the new store model."**
   - It turns the labor-reset thesis into a dated, falsifiable variance: +$0.28-0.47/sh from 1H FY27 alone if margin is merely flat.
   - It is memorable because consensus prices the FY27 recovery only as a 2H lap of a trough. That gives management two prints (Q3 FY26 personnel line, Q4 FY26 SG&A leverage) to prove savings before the 1H FY27 numbers are tested.
   - It is a calculation, not new primary data.
2. **WA4-2: the New York 2027 minimum-wage freeze.** It is a genuinely new, hard, dated fact about DKS's 4th-largest store state. It is small in dollars, but it rebuts "wage pressure is re-accelerating" with a concrete event.

## Evidence against / caveats
- BBG segment consensus rows are internally inconsistent: OI/rev vs the margin rows; GP vs GM%; Q2 FY27E revenue +6.6% on a 2.24% comp (D07). WA4-1's size ranges from −46 to −76bp depending on the row, and the GM-vs-SG&A attribution is not recoverable.
- A down-y/y 1H FY27 consensus is partly rational:
  - 1H FY27 laps a +5.4% comp with only ~2.3% comp expected, so occupancy and fixed costs deleverage;
  - D02 shows Q1 FY27 diesel +19% y/y, 2027 employer healthcare +8.2%, and freight still elevated;
  - promotions may persist into 1H FY27 (primer variance #1, −$0.45 probability-weighted).
  - So "flat margin" is an upside scenario, not a base case.
- Minimum-wage AGAINST points:
  - FL $15 (9/30/26), MI $15 and VA $13.75 (+7.7%) hit 117 stores (13% of the fleet) in or right before FY27;
  - local minimums (Seattle $22.14, Twin Cities > $17) are excluded and understate the level;
  - the NY freeze may be reversed by Hochul's proposed fix.
- No evidence of union organizing at DKS stores in news RSS. The NLRB case search was unreachable (connection reset), so absence is not proven.

## Avenue assessment
| Avenue | Access | Signal 1-5 | Script / path |
|---|---|---|---|
| W05C 8-K press releases (full read) | open | 2 (no personnel line; useful for the capex split and guidance timing) | — |
| W20 sector/macro (full read) | open | 1 | — |
| BBG segment consensus half-year decomposition | open | 4 (thesis #2 timing) | scripts\WA4_consensus_halves.py → raw\WA4_consensus_halves.csv |
| DOL WHD state minimum-wage page + Wayback CDX snapshots | open | 3 | scripts\WA4_minwage.py → raw\WA4_minwage_*.csv, raw\WA4_dol_state_*.html |
| Google News RSS (2027 minimum-wage announcements) | partial (SSL EOF throttling after ~10 queries) | 3 | scripts\WA4_news_rss.py → raw\WA4_news_rss.json |
| Bing News RSS | open (the Bing *web* RSS ignores the query, so useless) | 3 | scripts\WA4_bing.py → raw\WA4_bing.json |
| State labor sites (doli.virginia.gov, dlt.ri.gov) | open | 4 (authoritative) | inline in WA4_minwage.py SRC27 |
| NLRB case search | blocked (connection reset); not bypassed | — | — |
| MSN-hosted articles (Nebraska Examiner syndication) | blocked (JS-rendered) | — | — |

## Leads for next wave
- **L5 (cost model):** use WA4-1's half-year profile as the consensus base. Model 1H FY27 personnel % against 1H FY26's 14.25%. The variance sits in 1H FY27 (consensus −46 to −76bp y/y), not just the full year.
- **Q3 FY26 10-Q (~early Dec):** DICK'S personnel y/y bp. If it is ≤ +15bp (vs +44bp in 1H), WA4-1's 1H FY27 consensus is too low. Also check whether the remaining ~$5.7M redesign charge lands in Q3 or Q4.
- **Minimum wage, to firm up WA4-3:**
  - Nebraska DOL 2027 rate (dol.nebraska.gov; the Nebraska Examiner article "29 cents less than voters called for", 2026-09-23);
  - Vermont / South Dakota / Montana 2027 indexation releases;
  - Oregon July-2027 and Florida Sept-2027 CPI resets;
  - DKS store counts in Seattle, Denver, Twin Cities and Chicago (local minimums) for a local-adjusted version;
  - Hochul's NY "fix" (watch for a special session or the 2027 budget).
- **DKS entry pay vs floors:** L3's posted pay ranges in FL, MI and VA vs $15 / $15 / $13.75 show whether those steps bind. If DKS posts ≥$15.50 there, the AGAINST point in WA4-3 fades.
- **NLRB:** retry https://www.nlrb.gov/search/case (search "Dick's Sporting Goods", "Golf Galaxy") from a non-blocked route, or the NLRB public election-reports data files (https://www.nlrb.gov/reports/graphs-data), only if they are reachable without a challenge.

## Dead ends / blocked
- NLRB case search: TCP connection reset (bot protection). Stopped; not bypassed.
- EPI minimum-wage tracker: 403. Stopped.
- MSN article bodies: JS-rendered, no text. Bing web-search RSS ignores the query string.
- Google News RSS began returning SSL EOF errors after ~10 queries; I switched to Bing News RSS.
- W05C/W20 contain no store-labor hours, headcount, wage-rate or labor-program data. W20's wage-growth chart (BI, Atlanta Fed) is image-only, with no values.
- No news of union or organizing activity at DICK'S, Golf Galaxy or GGG stores (Bing News, 4 queries).

STATUS: COMPLETE
