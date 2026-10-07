# WA3 (wave 2): sweep of W05_DKS_8K_PRESSRELEASES_A.md + _B.md for thesis #2 (store-cost reset) and thesis #1 (HoS/FH)
Agent WA3 | 2026-10-07 | Files read in full: WORKING_NOTES\W05_DKS_8K_PRESSRELEASES_A.md (lines 1-1514; 8-Ks Nov-2022 to Nov-2024) and W05_DKS_8K_PRESSRELEASES_B.md (lines 1-739; 8-Ks Mar-Jul 2025). These are almost entirely earnings-release financial statements, FL deal and financing exhibits, and governance filings. They contain no store-labor-model text. My value-add is (a) the FY23 "business optimization" precedent (BURIED), (b) the restated non-GAAP SG&A history, which lets me split SG&A into personnel and non-personnel, and (c) a fresh labor-intensity series (personnel per sq ft, deflated by BLS retail wages).
Novelty checked by Grep against CORE_NOTES\00_CORE_DIGEST.md, FL_EUROPE_SCRAPE\baseline\primers\*, KNOWN_BRIEF.md and THESIS_SCRAPE\wave1\*.md / wave2\*.md.
Script: THESIS_SCRAPE\scripts\WA3_personnel_intensity.py → raw\WA3_personnel_intensity.csv; BLS pull → raw\WA3_bls_ahe.json (CES4200000003 retail AHE, all employees; CES4200000008 production/nonsupervisory; https://api.bls.gov/publicAPI/v1/timeseries/data/, accessed 2026-10-07).
Constants: FY27E DSG revenue $15,203M (FY26E $14,753M, so +3.05%); 10bp of DSG margin = $15.2M = $0.124/sh; $1M pre-tax = $0.00814/sh.

## Top findings

[WA3-1] **Labor intensity, measured as personnel $ per sq ft net of retail wage growth, has spiked twice: FY23 and 1H26. The FY23 spike barely reversed. At constant intensity, consensus FY27 sales growth of +3% cannot deliver personnel leverage.** Fresh series for the DICK'S business:

| | FY22 | FY23 | FY24 | FY25 | 1H26 (y/y) |
|---|---|---|---|---|---|
| Personnel $M (10-K Note 16/17; D07 quarterly for 1H) | 1,634.5 | 1,838.6 | 1,869.3 | 1,972.9 | 1,029.9 |
| Personnel $ growth (53rd-wk adj.) | | +12.5% (+10.4%) | +1.7% (+3.6%) | +5.5% | +9.3% |
| Sales growth (52-wk adj.) | | +3.6% | +4.9% | +5.0% | +6.0% |
| Personnel $/sq ft (year-end sq ft) | $38.4 | $43.1 ($42.2 adj) | $42.9 | $43.4 | |
| Personnel/sq ft growth (52-wk adj.; FY25 on restated FY24 44.8M sq ft; 1H26 assumes sq ft +2%) | | +10.1% | +1.5% | +3.9% | +7.2% |
| BLS retail AHE growth (fiscal-year average, Feb-Jan; 1H = Feb-Jul) | | +3.8% | +2.6% | +4.0% | +3.7% |
| **Implied labor intensity (hours per sq ft proxy)** | | **+6.3%** | **−1.1%** | **−0.1%** | **+3.5%** |

- FY23 was the store-payroll investment year. Intensity rose ~6%, and only ~1pt came back in FY24. That fits D07's "never reversed".
- 1H26 is a second, smaller spike (+3.5%). It coincides with the Q3FY25 opening wave (13 HoS + 6 FH), the five Q2 HoS openings and the Built to Win transition (training and role changes).
- Building on F5's numbers: WF's unit model puts HoS labor at 168 × $33K = $5.5M, which is 15.7% of $35M year-1 sales vs the fleet's 13.98%. So format mix pushes the ratio up structurally. INFERENCE: if each HoS replaces a ~$15M legacy box at ~14%, the incremental personnel ratio is ~17%.
- **FY27 arithmetic (INFERENCE):**
  - Hold intensity flat, with sq ft +2.5% (WF FY27E HoS/FH/legacy sq ft 41.4M → 42.4M) and wages +3% (BLS retail AHE Jul-Sep 2026 run-rate ~+3%). Personnel then grows ~+5.6% vs consensus DSG sales +3.05%. That is a **~35bp personnel deleverage**.
  - Consensus nonetheless has DSG margin +29bp. So consensus implicitly needs either labor intensity to fall ~2.5% (i.e., Built to Win working) or sales above +3%.
  - Thesis #1 and #2 are therefore one trade. With a 4% core comp, leverage comes automatically. With a 2.3% comp, the margin line in consensus is only reachable if the store redesign takes out hours.
- Variance:
  - Each 1% cut in hours/sq ft on a ~$2.19B FY27E personnel base (14.4% × $15,203M) is ≈ $22M ≈ 14bp of DSG margin ≈ **$0.18/sh**.
  - Fully reversing the 1H26 +3.5% spike is ≈ $77M ≈ 50bp ≈ $0.62/sh gross. Net of what consensus already needs (~2.5%), the residual upside is ~1pt ≈ +$0.18/sh. This is smaller than the gross figures in D07/F6.

| FY22-1H26 | W01 › 10-K FY24 Note 16 / FY25 Note 17; W05A/B › 8-K store tables (sq ft) and 53rd-week sales $170.2M; D07 raw\D07_dsg_cost_lines.csv; BLS API | accessed 2026-10-07 | method: python (scripts\WA3_personnel_intensity.py) | NEW calc (personnel % series DUP; the per-sq-ft/wage-deflated intensity series and the FY27 constant-intensity test are new) | conf M (year-end sq ft; FY23 53rd-week personnel pro-rated 52/53; retail-wide AHE is a proxy for DKS wages; GameChanger payroll sits inside personnel, see WA3-5) | SUPPORTS (1H26 spike is identifiable, not secular) / AGAINST (consensus already needs ~2.5% productivity; the FY23 spike stuck) | thesis #2 (links to #1) | ~+$0.18/sh residual base case; gross range −$0.30 to +$0.62.

[WA3-2] **DKS has run this playbook before: the FY23 "business optimization" precedent. Its savings were explicitly reinvested, but personnel $ was then held to +1.7% the next year.**
- Program sizing:
  - 8-K 2023-08-22 (Item 2.05): DKS eliminated positions "primarily at customer support center" (HQ) and expected ~$20M of severance in Q3 FY23.
  - The 8-K said "Related cost savings expected **largely offset by strategic talent investments** over next 12 months". The program aimed to "align talent, org design and spending… streamline cost structure".
  - The final FY23 program was $84.8M (8-K 2024-03-14): $26.7M severance, $46.1M store and intangible impairments (outdoor specialty, Moosejaw, Public Lands) and $12.0M inventory write-downs. Q3 was $52.5M ($23.3M severance) and Q4 $32.3M.
- Guidance language: the FY24 outlook release (2024-03-14, Hobart) said DKS will "grow both our sales and earnings through positive comps, higher merchandise margin and **productivity gains**". The Q2 FY24 release cited "SG&A leverage".
- Outcome in FY24:
  - Personnel $ +1.7% (+3.6% adjusting for the 53rd week) vs sales +3.5% (+4.9% adj.) on a 5.2% comp.
  - Personnel % −25bp (−17bp adj.). Intensity −1.1% (WA3-1).
- Read-across to Built to Win:
  - The FY26 charge (~$21M, of which $15.3M is severance/training) is the same order of size as FY23's $26.7M severance.
  - Both programs were framed as reinvestment ("talent investments" in 2023; "3,200 new leadership opportunities" in 2026).
  - In 2023 the reinvestment was real: non-personnel SG&A rose (WA3-3). But the personnel line itself did lever the following year.

| Aug-2023 to FY24 | W05A › SRC 8-K 2023-08-22 cover (Item 2.05) and EX-99.1; 8-K 2023-11-21 EX-99.1; 8-K 2024-03-14 EX-99.1 (SOURCE\01_DKS_SEC_FILINGS\8-K\...) | accessed 2026-10-07 | method: read + arithmetic | BURIED (the digest/primer have only "~$20M severance"; the "largely offset by talent investments" language, the $84.8M / $26.7M breakdown and the "productivity gains" guide are not surfaced) | conf H (facts), M (causality) | SUPPORTS (DKS has delivered personnel leverage after a reset) / AGAINST (savings explicitly recycled) | thesis #2 | variance: if FY27 repeats FY24 (personnel growth ~1.3pt below sales growth), that is ≈ −17 to −25bp of personnel % ≈ +$26-38M ≈ **+$0.21-0.31/sh** before netting consensus's assumed leverage (see WA3-1: net ≈ +$0.10-0.20).

[WA3-3] **The SG&A deleverage of FY24-FY25 came from NON-personnel lines: DKS has consistently re-spent leverage on tech and marketing.** DICK'S business, non-GAAP (ex deferred comp, ex optimization; FY23 restated for the grand-opening ad reclass):

| | FY23 | FY24 | FY25 |
|---|---|---|---|
| Total SG&A % of sales | 23.85% | 24.33% (+48bp) | 24.74% (+41bp) |
| Personnel % | 14.16% | 13.91% (−25bp) | 13.98% (+7bp) |
| **Non-personnel SG&A %** | **9.69%** | **10.42% (+73bp; $ +11.4%)** | **10.76% (+34bp; $ +8.3%)** |

- The FY25 10-K describes the extra SG&A as "technology, talent, marketing", partly offset by lower incentive comp.
- So before 2026, personnel was under control and the leak was tech, marketing and GameChanger/DMN build.
- This has two implications:
  - The 1H26 personnel spike breaks a two-year pattern. That supports reading it as transitory.
  - The "other expense snapback" leg of thesis #2 (World Cup roll-off, D07-4) runs against a 2-year structural rise of ~+50bp/yr in non-personnel SG&A. DKS has never let SG&A lever in aggregate since FY22, even on 5.2% and 4.5% comps.

| FY23-FY25 | W05B › 8-K 2025-03-11 EX-99.1 non-GAAP recon (FY24 3,270,635; FY23 3,096,741); W01 › 10-K FY25 MD&A (DICK'S SG&A +$219.9M, −41bp) + Note 16/17 personnel | accessed 2026-10-07 | method: arithmetic (SG&A − personnel; personnel is store/field/admin/GameChanger payroll inside SG&A per the 10-K definition) | NEW calc / BURIED inputs | conf M (FY23 includes the 53rd week; "non-personnel" includes advertising, bank card, eComm platform, tech and the CSC) | AGAINST (aggregate SG&A leverage is not DKS's habit) / SUPPORTS (personnel spike is new) | thesis #2 | variance: if non-personnel SG&A keeps rising +30-50bp/yr, it consumes the WC roll-off (~22bp) plus some of the personnel gain. Risk ≈ −$0.25-0.40/sh vs a "both legs lever" bull case.

[WA3-4] **Grand-opening marketing makes up roughly 30% of "pre-opening".** From 2024, DKS moved grand-opening advertising from SG&A into pre-opening and restated prior years.
- Restated pre-opening:
  - FY22: $21.7M vs $16.1M reported, so $5.6M was grand-opening ads.
  - FY23: $67.8M vs $47.3M, so **$20.6M**, i.e. 30% of the line.
  - Q2 FY23 alone (7 HoS conversions plus 10 DSG relocations): $32.9M vs $22.1M, so **$10.8M** of grand-opening marketing in one quarter. That is ≤ ~$1.5M per HoS opening (INFERENCE, upper bound; relocations share it).
- Later years: pre-opening was $57.5M in FY24 (7 HoS) and $69.0M in FY25 (16 HoS; DICK'S +$9.8M).
- Read-across: the pre-opening line is partly discretionary marketing, not just rent and payroll. Consensus has FY27E pre-opening at $86.9M ≈ FY26E $87.1M (F4), so this is no roll-off tailwind; NEUTRAL. It matters only if DKS cuts grand-opening events as openings normalize.

| FY22-Q2FY23 | W05A › 8-K 2024-09-04 and 2024-11-26 EX-99.1 reclass notes; W01 › 10-K FY24 (FY22 restated 21,686) | method: arithmetic | BURIED | conf H | NEUTRAL | thesis #2 (pre-opening) | ≤ ±$0.03/sh.

[WA3-5] **Caveat and lead: GameChanger payroll sits inside SG&A, and probably inside segment "personnel".** The 10-K defines SG&A as including "store/field/admin/**GameChanger payroll**", and segment personnel as "store & admin wages/comp within SG&A".
- So part of the +44bp 1H26 personnel deleverage may be GameChanger engineering headcount for a ~40%-CAGR business, not store labor.
- INFERENCE: if GC payroll is ~$60-80M growing ~25-30%, it adds ~+$8-10M per half, i.e. ~10-15bp of the 44bp.
- That cuts both ways:
  - Less of the spike is store labor, so the store redesign has less to recover.
  - Store labor alone delevered less than feared.

| W01 › 10-K FY25 MD&A "Company-specific definitions" + Note 17 footnote (2) | BURIED (grep "GameChanger payroll" = 0 hits in digest/primers/wave files) | conf L on the size | NEUTRAL | thesis #2 | lead for L5: size GC headcount (LinkedIn employee counts, GameChanger careers page) before attributing the spike to stores.

[WA3-6] **Thesis #1 caveat (comp quality of the early HoS cohort).**
- The 7 HoS opened in Q2 FY23 were "converted from prior combo store locations". A combo store is a DSG with an adjacent specialty box and a pass-through.
- The Q4 FY22 Field & Stream exit closed 12 of 17 F&S stores "for conversion into 8 DICK'S House of Sport + 4 expanded DICK'S stores". The charge was $30.1M: $28.5M impairments, $0.8M severance, $0.7M inventory.
- FY25: 5 Public Lands closures became 3 HoS + 2 FH.
- Since FY22 the comp includes relocated stores. If a converted HoS's comp base is the old DSG half only, part of the "HoS lift" for the 2023 cohort is absorbed adjacent-box volume. INFERENCE; the treatment is not disclosed.

| FY22-FY25 | W05A › 8-K 2023-03-07 EX-99.1 fn; 8-K 2023-08-22 EX-99.1 store notes; W05B › 8-K 2025-03-11 EX-99.1 fn 5 | BURIED (F&S → 8 HoS detail; Public Lands conversions already in F1) | conf L | AGAINST (minor) | thesis #1 | none quantifiable.

## Smoking-gun candidates
1. **WA3-1, the constant-intensity test.** "At +3% sales, +2.5% sq ft and +3% wages, DKS's personnel line delevers ~35bp unless labor hours per sq ft fall. Consensus has margin up 29bp. The Street is therefore already counting on Built to Win, or it is too low on comp. The only labor-intensity spike since FY23 is 1H26 (+3.5%), coinciding with the redesign and the Q3FY25 HoS wave." This is a fresh, reproducible calc from filings plus BLS. It reframes the two theses as one internally consistent trade, and it is honest about how much is already in consensus.
2. **WA3-2, the company's own precedent.** After the FY23 HQ RIF and payroll step-up, FY24 personnel $ grew only +1.7% (+3.6% adj.) on a 5.2% comp, which management had guided as "productivity gains". This is the closest DKS-specific analog for Built to Win, at a similar severance size ($26.7M vs ~$21M).

## Evidence against / caveats
- The FY23 intensity step-up (+6.3%) only reversed by ~1pt in FY24. DKS's labor investments tend to persist (WA3-1).
- In 2023 management explicitly said the RIF savings would be "largely offset by strategic talent investments". Built to Win is likewise framed as reinvestment (>3,200 leadership roles) (WA3-2).
- Non-personnel SG&A has risen +73bp and +34bp in FY24/FY25 on strong comps. DKS has not let aggregate SG&A lever since FY22 (WA3-3).
- HoS labor at year-1 sales (WF: 15.7%) runs above the fleet's 13.98%. Each relocation adds structural personnel deleverage until the store ramps (WA3-1, building on F5).
- GameChanger payroll inside personnel muddies the store-labor read (WA3-5).
- FY25 had "lower incentive comp" (10-K). The FY26 guide cut likely lowers 2H26 accruals again, and FY27 has a rebuild risk (already in KNOWN_BRIEF; restated here only as context).
- LTI design (8-K 2025-03-27): FY25-26 PSU metrics are total sales, adjusted EBT, external merchandise margin % and eCommerce growth. There is no SG&A or labor-productivity metric, though adjusted EBT is indirectly one. EVP Stores Ray Sliva was an NEO with a $1.25M target in 2025 (he was not in the 2023 NEO list), which signals that store operations were elevated. NEUTRAL.

## Avenue assessment
| Avenue | Accessibility | Signal 1-5 | Script / path |
|---|---|---|---|
| W05A (8-Ks Nov-22 to Nov-24: earnings releases, convert unwinds, governance) | open, read in full | 2 (thesis #2: business-optimization precedent, reclass, SG&A history; no store-labor text) | — |
| W05B (8-Ks Mar-Jul 25: Q4FY24/Q1FY25 releases, FL deal/pro forma/financing) | open, read in full | 1-2 (non-GAAP SG&A FY23/FY24, store tables, LTI metrics; FL pro forma not in scope) | — |
| BLS CES API v1 (retail AHE) | open (NAICS 4511-level series IDs tried, CES4245100003 / CES4245110003, do not exist) | 3 | raw\WA3_bls_ahe.json |
| Cross-file calc (10-K personnel + 8-K SG&A + sq ft + BLS) | open | 4 | scripts\WA3_personnel_intensity.py → raw\WA3_personnel_intensity.csv |

## Leads for next wave
- **L5 (cost model):** use raw\WA3_personnel_intensity.csv as the intensity baseline. Add Q3FY26 when the 10-Q lands (~early Dec): a quarterly intensity print below +1.5% would be the "proof" datapoint. Model consensus FY27 with explicit sq ft (+2.5%) and wage (+3%) inputs to show the implied productivity.
- **GameChanger headcount:** LinkedIn company page employee count for GameChanger (2024 vs 2026), and GC careers postings. Needed to strip GC payroll out of segment personnel (WA3-5).
- **10-K human capital (WA1 territory):** full-time/part-time headcount FY22-FY25. Combined with personnel $ it gives cost per employee vs BLS. That would split the FY23 spike into heads vs pay.
- **W05C (WA4):** check the 2026-03 LTI 8-K. Did FY26-27 PSU metrics add an SG&A, labor or EBIT-margin metric after Built to Win? A new metric would signal board-level commitment to the savings.
- **Q3 FY26 call (Nov 24-25):** ask whether Built to Win savings are being "reinvested" (the 2023 wording) or flowing through.

## Dead ends / blocked
- No store-labor, staffing, wage or "operating model" language anywhere in W05A/B. The 8-K releases of this period do not discuss store payroll.
- BLS NAICS 4511 (sporting goods stores) AHE series are not published under the IDs tried, so I used all-retail AHE as the proxy.
- The FL pro forma (W05B SRC 14/18) gives FL SG&A of $2.1B on $7.99B. That is out of scope (FL is excluded from thesis #2 and FL closures are excluded topics).

## Duplicates skipped
~$20M Aug-2023 severance and the −24% stock reaction (digest/primer); personnel % FY22-FY25 and the quarterly series (KNOWN_BRIEF/D07); construction-allowance history (D07-6/F6-5); pre-opening quarterly figures and the FY26 ~$90M guide (digest/F3/F4/F5); HoS/FH conversion counts FY24 (F2); comp-definition changes (relocations from FY22, GameChanger FY24, Warehouse Sale FY25; known via WF "+110bps"); WF HoS 168 employees / $33K (F5/F6); FL deal terms, $100-125M synergies, pro forma EPS; Stack's 2023 "growth opportunities… since we went public" quote (in C05, a quote only, not evidence).

STATUS: COMPLETE
