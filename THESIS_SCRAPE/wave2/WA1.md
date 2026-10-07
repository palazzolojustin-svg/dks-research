# WA1 (wave 2): Working-notes sweep of DKS 10-Ks FY22-FY25 (W01, W02) + Annual Reports to Shareholders (W09)
Agent WA1 | 2026-10-07 | Files read IN FULL: WORKING_NOTES\W01_DKS_10K_FY2024-FY2025.md (l.1-965), W02_DKS_10K_FY2022-FY2023.md (l.1-441), W09_DKS_ANNUAL_REPORTS_TO_SHAREHOLDERS.md (l.1-212). Key numbers verified in SOURCE\01_DKS_SEC_FILINGS\10-K\*.md (line refs below) and SOURCE\04_PEERS\FL\sec_filings\FL_10-K_FY2024 (FL FT/PT mix).
Novelty: every item Grep-checked against CORE_NOTES\00_CORE_DIGEST.md, FL_EUROPE_SCRAPE\baseline\primers\*, KNOWN_BRIEF.md, THESIS_SCRAPE\wave1\*.md and wave2\* (other wave-2 files were still stubs at check time).
Script: THESIS_SCRAPE\scripts\WA1_10k_labor_series.py → raw\WA1_10k_labor_series.csv
Variance constants: FY27E DSG revenue $15,203M; 10bp DSG margin = $15.2M = $0.124/sh; $1M pre-tax = $0.00814/sh.

## Top findings (ranked)

[WA1-1] **The FY25-26 personnel deleverage is a HEADCOUNT problem, not a wage-rate problem, which is exactly what a labor-model redesign can fix.** DICK'S Business employees at fiscal year-end: FY22 52,800 (18,800 FT / 34,000 PT), FY23 55,500 (18,900 / 36,600), FY24 56,100 (18,600 / 37,500), FY25 ~59,800 (105,200 total less 45,400 Foot Locker Business). FT share 35.6% → 34.1% → 33.2%.
- FY25 heads +6.6% (+3,700) vs DICK'S sales +5.0% and gross sq ft +1.6% (44.8M → 45.5M). FY24 heads were only +1.1%, on 52-week sales +4.9%.
- Personnel $ per average head (52-week basis): FY23 $33.3K, FY24 $33.5K (+0.6%), FY25 $34.0K (+1.6%). Pay per head has barely moved since the FY23 wage-rate step-up (WA1-4). FY25 personnel +5.5% therefore came almost entirely from heads, with "lower incentive compensation" also holding down pay per head.
- Heads per 1,000 gross sq ft: 1.252 (FY24) → 1.314 (FY25), +5.0%. Sales per FYE head: $239.6K → $235.9K (−1.5%), after +3.8% in FY24.
- INFERENCE (FT/PT split): applying Foot Locker's own FYE24 FT share (13,140 FT / 34,166 PT = 27.8%, FL 10-K FY2024 l.254) to the 45,400 FL heads gives DICK'S FY25 ≈ 19,000 FT (+2%) and ≈ 40,800 PT (+9%). The build was mostly part-time hours/coverage.
- INFERENCE (format vs non-format split of the FY25 +3,700). Inputs: WF staffing (HoS 168, FH 65; F5-4), a legacy DSG box at ~62 heads, GG ~18, GGG ~15, and the FY25 store table (HoS 13 relocations + 3 new; FH 13 relocations + 2 new; 7 DSG closed; GG +4; GGG +1 net).
  - Formats explain ≈ +1,700 heads (≈ +2,100 if HoS staff ≈ 200, per H03 Cedar Rapids).
  - That leaves ≈ +1,600 to +2,000 "non-format" heads: CSC/tech "talent", GameChanger, extra store coverage.
  - The same arithmetic for FY24 (HoS 6 relocations + 1 new; FH 11 relocations + 4 new; 6 DSG and 8 other closures; GG +5; GGG +4) gives a residual of ≈ −150. Non-format heads were flat in the post-Business-Optimization year and jumped in FY25.
- At $34K each, the FY25 non-format build ≈ $55-68M ≈ 39-48bp of FY25 DICK'S sales. That is the same size as the 1H FY26 +44bp personnel deleverage (KNOWN).

| FYE FY22-FY25 | SOURCE 10-K FY2022 l.365, FY2023 l.387, FY2024 l.413, FY2025 l.535 (headcount); FY2024 10-K segment note l.2883 and FY2025 10-K Note 17 l.3795 (personnel $); W01/W02 store tables | accessed 2026-10-07 | method: python (scripts\WA1_10k_labor_series.py) | BURIED (headcount series: 0 hits in digest/primers/KNOWN/wave files) + NEW calc | conf M. Caveats: FYE headcount is point-in-time and rounded to 100; it counts heads, not hours; the DICK'S total includes CSC, DCs and GameChanger; the FL subtraction assumes the 45,400 is FYE FL headcount (the 10-K says so); FY22/FY23 sq ft exclude Warehouse Sale space while FY24/FY25 include it | SUPPORTS | thesis #2 | variance (INFERENCE): if Built to Win removes 1/3 to 2/3 of the FY25 non-format build (≈550-1,300 heads × ~$35K = $19-45M), that is 13-30bp of FY27E DSG sales ≈ +$0.16-0.37/sh gross. Consensus already embeds ~+22bp of SG&A leverage, which leaves net upside of ≈ $0 to +$0.20/sh unless the WC marketing roll-off (D07-4) adds on top.

[WA1-2] **DKS's last severance-backed cost action is a clean analog. It levered personnel by 17-25bp the next year, about 0.9-1.3x the severance.**
- FY23 "Business Optimization" (positions eliminated "primarily at CSC", plus outdoor/Moosejaw): $84.8M pre-tax, of which $26.7M severance.
- The charges sat in corporate & other ($98.8M = $84.8M BO + $14.0M deferred comp), not in segment personnel. So DICK'S personnel 14.16% (FY23) is clean.
- FY23 10-K (filed 2024-03-28, l.982): "Following our Business Optimization actions, our selling, general and administrative expenses during the fourth quarter of 2023 have moderated by approximately 78 basis points as a percentage of net sales. In 2024, we expect selling, general and administrative expenses to leverage... driven by the future benefits from our Business Optimization actions and our ongoing focus on improving productivity".
- Outcome FY24: personnel 13.91% vs 14.16% (−25bp reported; −17bp vs a 52-week-adjusted FY23 of 14.08%). Personnel $ +3.6% vs 52-week sales +4.9%, heads +1.1%. The FY24 10-K says SG&A carried "higher incentive compensation", so the underlying leverage was larger than the print.
- Savings at FY24 sales ≈ $23-34M vs $26.7M severance.
- FY26 parallel: the $15.3M Q2 "store operating model redesign" charge (≈$21M FY) is also excluded from segment results (KNOWN). Built to Win targets STORE payroll, the bulk of the $1.97B personnel line, whereas BO was CSC-centric, so the base it acts on is larger.

| FY23-FY24 | SOURCE 10-K FY2023 l.982 (78bp quote), l.1137; W02 › Business Optimization note; W01 › Note 12/17; W09 › ARS 2024-05-02 non-GAAP recon | method: read + ratio | BURIED (78bp, the leverage guidance and the BO severance → personnel-leverage link: 0 hits; the digest only has "~$20M severance" at the Aug-23 guide cut) | conf M-H on the data, M on the analogy | SUPPORTS | thesis #2 | variance (INFERENCE): 0.9-1.3x payback on ~$21M ⇒ $19-27M/yr ≈ 12-18bp of FY27E DSG sales ≈ +$0.15-0.22/sh gross. FY24 achieved −17 to −25bp on a +5.2% comp. Achieving the same on consensus's ~2.6% FY27 comp would need about twice the structural saving. On the analog alone, thesis #2 reaches roughly consensus's ~22bp. Upside beyond consensus needs a larger store-level scope (WA1-1) and the marketing roll-off.

[WA1-3] **AGAINST (reinvestment risk): last time, the SG&A leverage DKS guided to never showed up in total SG&A. Only the personnel line levered.** After guiding to FY24 SG&A leverage "driven by... Business Optimization", non-GAAP SG&A went from 23.85% (FY23) to 24.33% (FY24), +48bp (ratios DUP from digest l.35). The FY24 10-K explains: "strategic investments across technology and marketing, along with higher incentive compensation" (SOURCE 10-K FY2024 l.1207). The savings were spent. The FY27 risk is the same: Built to Win creates ">3,200 new leadership opportunities" and Specialist roles (KNOWN), so headcount savings may be recycled into pay rates or service.
| FY23-FY24 | SOURCE 10-K FY2024 l.1207; FY2023 l.982 | method: read | BURIED (the juxtaposition of guidance and outcome is new; the ratios are DUP) | conf H | AGAINST | thesis #2 | variance: argues for haircutting gross savings by ~30-50% in the bull case.

[WA1-4] **The 14%+ personnel ratio was built by disclosed wage-rate investments in FY22-FY23, which are now behind DKS.**
- FY22 SG&A: "$127.1 million increase was primarily driven by investments in hourly wage rates, talent and technology", offset by lower incentive comp.
- FY23: "$191.7 million of investments in hourly wage rates, talent and technology" plus $66.0M of marketing (brand-building and HoS grand openings).
- Together: $318.8M ≈ 2.5% of FY23 sales. Personnel went from 13.22% (FY22, $1,634.5M; FY24 10-K segment note l.2883) to 14.16% (FY23; +86bp on a 52-week basis). Pay per FYE head rose ≈ +5.0% and heads +5.1%.
- From FY24 onward, pay-per-head growth fell to +0.6-1.6% (WA1-1), and retail wage growth is slowing (+2.9-3.1%; KNOWN D02). The rate component that built the step-up has stopped compounding. What is left is heads/hours (WA1-1).
| FY22-FY23 | SOURCE 10-K FY2022 l.1094; FY2023 l.1137; FY2024 l.2883 | method: read + ratio | BURIED ($127.1M/$191.7M "hourly wage rates": 0 hits; the FY22 13.22% ratio is DUP from D07) | conf H | SUPPORTS (context) | thesis #2 | variance: none directly. Supports the bull case that FY27 personnel growth can run at about wage inflation (~3%) plus format heads, i.e. at or below sales growth.

[WA1-5] **AGAINST: incentive-comp swings are large enough to absorb much of the FY27 saving.** The best proxy is accrued "payroll, withholdings & benefits":
- FY21 $297.4M → FY22 $218.8M (MD&A: "lower incentive compensation") → FY23 $213.0M → FY24 $256.9M ("higher incentive compensation", +$43.9M) → FY25 $397.7M (includes FL; MD&A: "lower incentive compensation").
- Swings of $44-79M equal ≈ 30-60bp of DICK'S sales.
- After the FY26 guide cut (August), the FY26 bonus accrual is probably low, so a return to target in FY27 could re-add ~20-40bp of personnel (INFERENCE). This quantifies the KNOWN "incentive-comp rebuild" caveat.
| FY21-FY25 | W01 › Note 6; W02 › accrued expenses; SOURCE 10-K FY2024 l.1207, FY2025 l.1472 | method: read + arithmetic | BURIED/NEW calc | conf L-M (the accrual mixes payroll-timing effects; FY25 includes FL) | AGAINST | thesis #2 | variance: −$0.25 to −$0.50/sh headwind if the bonus fully rebuilds (INFERENCE). It nets against WA1-1/2.

[WA1-6] **401(k) match growth points to a FY25 build skewed to higher-paid (salaried/talent) roles, the layer Built to Win de-layers.**
- DICK'S Smart Savings Plan employer match, under the same safe-harbor formula since 1/1/2022 (100% up to 4% + 50% of the next 2%): FY21 $24.1M (old 75% discretionary match), FY22 $31.6M, FY23 $34.8M (53 weeks, +10.1%), FY24 $36.7M (+5.5%), FY25 $41.2M (+12.3%).
- FL plans are reported separately ($4.8M). Matched comp grew ~2x as fast as total personnel (+5.5%) in FY25.
- Read: either higher-paid hires (CSC/tech "talent", store leadership) or higher participation.
- Caveat AGAINST the read: a Roth option was added on 2024-05-03, which may have lifted participation.
| FY21-FY25 | SOURCE 10-K FY2025 l.3686; W01 › Note 15; W02 › retirement | method: read + ratio | BURIED (0 hits) | conf L-M | SUPPORTS (weak) | thesis #2 | variance: none directly.

[WA1-7] **The redesign was a planned, 12+-month program: the filings telegraphed it before the April 2026 release.**
- The FY24 10-K (filed 2025-03-27, l.567) added "organizational re-alignment" to the strategic-initiatives risk factor: "improving teammate productivity through strategic talent investments, organizational re-alignment". The FY23 10-K l.534 had only "strategic talent investments".
- The FY25 10-K (l.703) adds "may require higher short-term expenditures".
- Julie Lodge-Jarrett's title became "Chief People, Purpose and Transformation Officer" effective March 2025, "responsible for strategy and transformation teams... to transform the business" (FY25 10-K l.601).
- EVP-Stores Ray Sliva (since Jan 2023): 23 years at Best Buy, including Chief People Officer and President of Retail. He replaced Don Germano (EVP Stores & Supply Chain; separation agreement is FY23 10-K Exh. 10.8).
- OUTSIDE KNOWLEDGE, unverified here: Best Buy reworked its store workforce model in 2020-21. That is a lead for L4.
| Mar-2025 to Mar-2026 | SOURCE 10-K FY2023 l.534; FY2024 l.567; FY2025 l.601, l.703; W01 › exec officers; W02 › exhibits | method: cross-year text diff | BURIED/NEW (0 hits for re-alignment/Transformation/Germano) | conf H on the text, L on the implication | SUPPORTS (qualitative: a deliberate cost program, not a reactive cut) | thesis #2 | variance: none directly.

[WA1-8] **Thesis #1: landlords fund about 1/4 of DICK'S capex once receivables are counted, not the 10-17% the cash-only series shows. A $274M landlord receivable is still to be collected.**
- Accounts receivable due from landlords: $45.0M (FYE21), $34.3M (FYE22), $72.7M (FYE23), $160.2M (FYE24), $274.0M (FYE25, consolidated).
- Landlord funding earned = cash allowances received + Δ landlord AR: FY22 $25.4M (7.0% of DICK'S capex) → FY23 $105.5M (18.0%) → FY24 $163.8M (20.4%) → FY25 $275.5M (26.4% of DICK'S capex of $1,043.5M).
- This extends F6-5/D07-6/F4-5, which used cash received only (9.9/11.4/9.5/14.2%).
- It also explains the record 1H26 cash receipts (Q1FY26 $71.7M, KNOWN F6-5): they are the FYE25 receivable converting to cash.
| FYE21-FYE25 | SOURCE 10-K FY2023 l.1969, FY2024 l.2016, FY2025 l.2450; W01/W02 cash flows | method: python | BURIED (AR series: 0 hits) + NEW calc | conf M (the FYE25 AR includes FL; FL's share is unknown but FL had few new stores and Fast Break remodels) | SUPPORTS | thesis #1 (returns/landlord demand) | variance: FCF/returns only. It supports the "landlords pay up for HoS" claim; no EPS effect.

[WA1-9] **Thesis #1 caveat: the space roll-out under-delivered against the 10-K plan, and the new formats are more labor-dense.**
- The FY24 10-K (Mar-2025) said "approximately 70% of our 2025 store openings will be relocations or remodels... which will increase our square footage in 2025 by approximately 3%".
- Actual DICK'S Business gross sq ft: +1.6% (44.8M → 45.5M). FH openings were 15 vs a plan of ~18; GGPC 9 vs ~14 (HoS 16 as planned).
- Heads per 1,000 sq ft rose +5.0% in FY25 (WA1-1), consistent with WF's 1.4 heads/K sq ft for HoS vs ~1.2-1.25 for the chain.
- The FY24 10-K also dropped "new store productivity" from its store-productivity KPI list; the FY23 10-K l.1007 had it.
| FY25 | W01 › FY24 10-K liquidity (capex plan) vs FY25 store table; SOURCE 10-K FY2023 l.1007 vs FY2024 l.1074 | method: read + arithmetic | BURIED (the ~3% guide vs actual: 0 hits; F2 has the +1.3% actual) | conf H | AGAINST (mild; #1 execution, #2 structural labor intensity) | thesis #1/#2 | variance: none directly.

## Smoking-gun candidates
1. **WA1-1 (headcount, not wage rate).** A one-line exhibit: "DICK'S added ~3,700 heads in FY25 (+6.6%) on +1.6% space and +5.0% sales. Pay per head rose only ~1.6%. Formats explain under half, and the rest (~1,600-2,000 heads, ≈$55-68M, ≈40-48bp) is exactly what the April-2026 store-labor redesign attacks." It reframes the bear's "structural deleverage from big boxes" as mostly addressable. It is hard 10-K data and was never surfaced. It weakens if the Q3 FY26 10-Q personnel line does not improve.
2. **WA1-2 (Business Optimization analog), paired honestly with WA1-3.** DKS has done this before: a $26.7M severance action → 17-25bp of personnel leverage the next year, about 1x payback. The PM will also ask about the reinvestment history (WA1-3), so present the two together. They support "personnel will lever in FY27". They do not support "total SG&A will beat consensus" without the marketing roll-off (D07-4).

## Evidence against / caveats
- WA1-3: post-BO savings were reinvested; non-GAAP SG&A deleveraged +48bp in FY24 despite leverage guidance.
- WA1-5: incentive-comp rebuild in FY27 could be ~20-40bp (proxy, low confidence).
- Labor-density of the new formats is real: heads per K sq ft +5.0% in FY25 (WA1-9). FY27 still has ~14-20 HoS/FH openings, mostly relocations that add ~100+ heads per HoS.
- Labor-regulation risk is rising in the filings. "Teammate organizing efforts" became a risk-factor heading in the FY23 10-K (filed 2024-03, l.590); it was absent in FY22. The FY25 10-K (l.857) adds predictive "scheduling" laws, the PRO Act and NLRB priorities. These could limit how far store roles can be cut or flexed.
- The analog differs in scope: BO was CSC-centric while Built to Win is store-centric. Store roles carry service and comp risk (DKS's selling culture). Management frames Built to Win as an investment.
- Data limits: FYE headcounts are rounded snapshots of heads, not hours. FY25 DICK'S heads are derived by subtracting FL. FY25 landlord AR and accrued payroll include FL.

## Avenue assessment
| Avenue | Access | Signal 1-5 | Script / path |
|---|---|---|---|
| W01 (FY25/FY24 10-K notes) | open | 4 | segment Note 17, human capital, Notes 6/15, cash flow |
| W02 (FY23/FY22 10-K) | open | 4 | SG&A driver text ($127.1M/$191.7M), BO note, headcount, 401(k) |
| W09 (ARS letters + non-GAAP recons) | open | 2 | mostly DUP (HoS letter quotes = F4-6); recon confirms the BO and SG&A ratios |
| SOURCE 10-K cross-year text diff (risk factors, titles) | open | 3 | Select-String on SOURCE\01_DKS_SEC_FILINGS\10-K\*.md |
| FL 10-K FT/PT mix (to split FY25 DICK'S FT/PT) | open | 2 | SOURCE\04_PEERS\FL\sec_filings\FL_10-K_FY2024 l.254 |
| Computed series | open | 4 | scripts\WA1_10k_labor_series.py → raw\WA1_10k_labor_series.csv |

## Leads for next wave
- **L5 (cost model):** use WA1-1 inputs: FYE heads 52.8K/55.5K/56.1K/~59.8K; pay per avg head $33.3K/$33.5K/$34.0K; the format-vs-residual split (FY24 residual ≈ −150, FY25 ≈ +1,600-2,000). Add 1H26 personnel +9.7%/+9.0% to back out implied 1H26 heads/hours growth. At ~+2-3% pay per head, heads/hours ran ≈ +6-7% y/y in 1H26, still well above sq ft (+~2%).
- **Q3 FY26 10-Q (early Dec 2026):** DICK'S personnel $ y/y. Also look in the FY26 10-K (Mar 2027) for the FYE26 DICK'S headcount. A flat-to-down FY26 FYE headcount despite ~14 HoS/~20 FH would be the hard proof of WA1-1.
- **L4:** Ray Sliva's Best Buy tenure (dates as President of Retail / Chief People Officer) vs Best Buy's 2020-21 store workforce restructuring and the savings disclosed in Best Buy 10-Ks/calls. That would be a sized analog run by the same executive.
- **WA6/L5:** check whether the Q2 FY26 10-Q separates the $15.3M charge into severance vs training (the BO note gave severance $26.7M of $84.8M, with $9.6M unpaid at YE). An unpaid-severance accrual at 8/1/26 would size the headcount reduction (÷ ~$10-20K per role).
- **Proxy (DEF 14A 2026, filed ~Apr-May 2026):** FY26 annual-incentive metrics and payout scale. They would size the FY27 bonus-rebuild headwind (WA1-5) better than the accrued-payroll proxy.

## Dead ends / blocked
- No savings, hours or store-level labor figures appear in any 10-K or ARS (FY22-FY25). DICK'S FY25 FT/PT is not disclosed separately (estimated via FL's mix). FY21 personnel $ is not disclosed (the segment note starts with FY22), so the FY22 wage-rate step cannot be ratioed.
- W09 ARS content beyond the 10-Ks is CEO-letter color and non-GAAP recons. HoS letter quotes are already F4-6.

## Duplicates skipped
Signed-not-commenced leases $238.2M/$215.5M/$352.1M/$756.0M (F1-2); HoS ARS quotes "exceeded initial performance expectations" / "travel farther" (F4-6); cash construction allowances FY21-FY25 and % of capex (F6-5, D07-6, F4-5); advertising FY21-FY25 and gift-card breakage (D07-5); annual personnel % FY22-FY25 (D07-2); NG SG&A % FY22-FY25 (digest l.35); store tables, HoS/FH counts and plans, 75-100 target, FY26 plan ~14 HoS/~22 FH; HoS $35M/20% EBITDA; 1H/2H FY26 DICK'S margin guide and synergy timing (digest l.153/178); FL acquisition charges, $40-55M FL HQ charge, interchange $150M gain, $25M lease-termination gain; OBBBA cash-tax; SBC $57.3M/$71.0M/$123.7M; FY25 comp ticket +4.2%/transactions +0.3% (digest l.32); Nike ~31%; ~3/4 of DSG leases renewable within 5 years; lease terms 7.71 years.

STATUS: COMPLETE
