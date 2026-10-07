# DKS — Bloomberg ALTD Alternative Data Pack

**Ticker:** DKS US · **Px:** $136.08 (02-Oct-26 close) · **Next earnings:** 11/25/26 · **Source:** Bloomberg `ALTD <GO>` (screenshots, compiled 04-Oct-26)

**Labels:** `DISCLOSED` = read straight off the Bloomberg screen · `DERIVED` = computed from disclosed numbers · `INFERRED` = interpretation, verify before citing

---

## 0. Key takeaways

1. **The Foot Locker lap shows up in the weekly data.** DKS weekly transaction spend ran +15% to +58% YoY every week from w/e 05-Oct-25 through 06-Sep-26, then turned negative: **−3.3 / −2.4 / −3.3** (w/e 13/20/27-Sep). Foot Locker closed **8-Sep-25** (DKS 10-K), so 13-Sep-26 is the first lapped week. `DISCLOSED` data, `INFERRED` cause.
2. **After the lap, DKS still beats its sub-industry but only matches broad retail.** Last-3-week averages: DKS -3.0 vs Sporting Goods Stores -8.3 vs Retail-Disc -3.3. `DERIVED`
3. **The 2027 Q3 Second Measure estimate (45.97%) is a flat carry-forward of quarter-to-date data that is mostly pre-lap.** The PTD estimate has already fallen from 58.31% (day 7) to 45.97% (day 57), and it should keep falling as post-lap days come in. Consensus at 21.71% probably already includes the lap. Don't read the +24pt gap as a beat. `INFERRED`
4. **Second Measure missed in exactly the acquisition quarters:** −16.40pt (2026 Q3) and −13.15pt (2026 Q4). It was within ±3pt every other quarter. The model was slow on the step-up, so it may be slow on the step-down too. `DERIVED` / `INFERRED`
5. **4 of 5 alt-data sources say ~46–52% vs 21.7% consensus (Similarweb is the exception).** Independent sources agreeing that much points to a structural cause (M&A), not a real beat. `INFERRED`
6. **Facteus may be an organic DKS proxy.** It shows only a small step-up after the deal (~9pt vs ~28pt for Second Measure). Aug-26 was spend +2.3%, count flat, ticket +2.3% (§9b). `INFERRED`

---

## 1. Fiscal calendar (Bloomberg labels)

| BBG period | Period end | Notes |
|---|---|---|
| 2026 Q3 | 11/01/25 | Foot Locker closed 9/8/25, mid-quarter |
| 2026 Q4 | 01/31/26 | First full quarter with Foot Locker |
| 2027 Q1 | 05/02/26 | |
| 2027 Q2 | 08/01/26 | |
| **2027 Q3** | **10/31/26** | **Current. Starts 08/02/26; Foot Locker anniversary 9/8/26; earnings 11/25/26** |

BBG labels by the calendar year the fiscal year ends in. DKS calls the year ending Jan-26 "fiscal 2025."

---

## 2. Source scorecard — 2027 Q3 vs Revenue (`DISCLOSED`)

| Source | Metric | Channels | % of Qtr | PTD YoY | vs Cons (21.7) | R² 3Y | MAE 3Y |
|---|---|---|---|---|---|---|---|
| **Bloomberg Second Measure** | Transaction Spend | Online + In-Store | 63% (57/91 days) | 46.0% | +24.3 Above | **94.2%** | **3.8** |
| Facteus Arbiter | Transaction Spend | — | 55% | 51.6% | +29.9 Above | 86.2% | 5.5 |
| Placer.ai | Foot Traffic Visits | In-Store | 55% (50/91 days) | 49.0% | +27.3 Above | 85.1% | 5.9 |
| Similarweb | Web Traffic Visits | Web | 63% | 4.6% | −17.1 Below | 86.9% | 13.7 |
| Apptopia | App Time Spent | App | 55% | 47.6% | +25.9 Above | 61.2% | 12.6 |

**Adjusted vs. unadjusted fit:**

| Source | Adj R² | Adj MAE | Unadj R² | Unadj MAE |
|---|---|---|---|---|
| Second Measure | 94.23% | 3.76 | 98.21% | 13.22 |
| Placer.ai | 85.12% | 5.87 | 65.09% | 21.70 |

For Second Measure, unadjusted data tracks direction well but is off on level; the adjustment fixes the level. For Placer, the adjustment does most of the work. `INFERRED`

**Ranking:** Second Measure (primary) → Facteus (cross-check) → Placer (in-store support only) → skip Similarweb and Apptopia (MAE 12–14pt).

---

## 3. KPI Correlation — Second Measure (Adj.) vs Reported Revenue YoY (`DISCLOSED`)

Bloomberg states the estimate was **directionally accurate 8 of 8 periods**.

| Period | End | BSM Est (Adj) | Reported Rev YoY | Diff (BSM − Rev) |
|---|---|---|---|---|
| 2024 Q3 | 10/28/23 | 0.58% | 2.82% | -2.24 |
| 2024 Q4 | 02/03/24 | 6.75% | 7.77% | -1.02 |
| 2025 Q1 | 05/04/24 | 6.99% | 6.20% | +0.79 |
| 2025 Q2 | 08/03/24 | 4.82% | 7.75% | -2.93 |
| 2025 Q3 | 11/02/24 | 2.62% | 0.49% | +2.13 |
| 2025 Q4 | 02/01/25 | -0.11% | 0.45% | -0.56 |
| 2026 Q1 | 05/03/25 | 4.58% | 5.18% | -0.60 |
| 2026 Q2 | 08/02/25 | 7.63% | 4.98% | +2.65 |
| 2026 Q3 | 11/01/25 | 19.93% | 36.33% | -16.40 ⚠️ FL close |
| 2026 Q4 | 01/31/26 | 46.75% | 59.90% | -13.15 ⚠️ FL close |
| 2027 Q1 | 05/02/26 | 64.99% | 62.68% | +2.31 |
| 2027 Q2 | 08/01/26 | 52.86% | 53.21% | -0.35 |
| **2027 Q3** | **10/31/26** | **45.97%** | **—** | **Mean consensus 21.71%** |

Average absolute miss excluding the two acquisition quarters: **1.56pt**. Including them: **3.76pt**. `DERIVED`

---

## 4. Quarter-to-date daily build — 2027 Q3 (`DISCLOSED`)

### 4a. Second Measure (Adj.) — days 7–36 captured

| Day | Date | PTD (Adj) | Consensus | Diff |
|---|---|---|---|---|
| 7 | 08/08/26 | 58.31% | 23.88% | +34.43 |
| 8 | 08/09/26 | 58.60% | 23.88% | +34.72 |
| 9 | 08/10/26 | 58.36% | 23.88% | +34.48 |
| 10 | 08/11/26 | 56.91% | 23.86% | +33.05 |
| 11 | 08/12/26 | 56.42% | 23.86% | +32.55 |
| 12 | 08/13/26 | 56.20% | 23.86% | +32.33 |
| 13 | 08/14/26 | 55.75% | 23.86% | +31.89 |
| 14 | 08/15/26 | 55.30% | 23.86% | +31.43 |
| 15 | 08/16/26 | 55.40% | 23.86% | +31.54 |
| 16 | 08/17/26 | 55.01% | 23.86% | +31.15 |
| 17 | 08/18/26 | 55.14% | 23.86% | +31.28 |
| 18 | 08/19/26 | 54.56% | 23.83% | +30.73 |
| 19 | 08/20/26 | 54.69% | 23.72% | +30.96 |
| 20 | 08/21/26 | 55.03% | 23.72% | +31.30 |
| 21 | 08/22/26 | 55.10% | 23.72% | +31.37 |
| 22 | 08/23/26 | 54.46% | 23.72% | +30.74 |
| 23 | 08/24/26 | 54.62% | 23.68% | +30.93 |
| 24 | 08/25/26 | 54.68% | 21.97% | +32.71 |
| 25 | 08/26/26 | 54.42% | 21.82% | +32.60 |
| 26 | 08/27/26 | 54.44% | 21.74% | +32.69 |
| 27 | 08/28/26 | 54.23% | -5.24% ⚠️ | +59.47 |
| 28 | 08/29/26 | 55.11% | -5.24% ⚠️ | +60.35 |
| 29 | 08/30/26 | 55.63% | 21.66% | +33.97 |
| 30 | 08/31/26 | 54.20% | 21.66% | +32.55 |
| 31 | 09/01/26 | 54.76% | 21.66% | +33.10 |
| 32 | 09/02/26 | 54.62% | 0.30% ⚠️ | +54.33 |
| 33 | 09/03/26 | 54.55% | 0.30% ⚠️ | +54.26 |
| 34 | 09/04/26 | 54.93% | 21.62% | +33.30 |
| 35 | 09/05/26 | 54.57% | 21.62% | +32.95 |
| 36 | 09/06/26 | 54.61% | 21.62% | +32.99 |

| Day | Date | PTD (Adj) | Consensus | Diff |
|---|---|---|---|---|
| 37–56 | 09/07–09/26 | *not captured* | | |
| **57** | **09/27/26** | **45.97%** | **21.71%** | **+24.26** |

Days 58–91 on screen are a flat projection (45.97 / 21.71 / 24.26), not data. They're excluded here.

### 4b. Placer.ai (Adj.) — days 28–50 captured (50 = last actual day)

| Day | Date | PTD (Adj) | Consensus | Diff |
|---|---|---|---|---|
| 28 | 08/29/26 | 50.30% | -5.24% ⚠️ | +55.54 |
| 29 | 08/30/26 | 50.48% | 21.66% | +28.83 |
| 30 | 08/31/26 | 48.79% | 21.66% | +27.13 |
| 31 | 09/01/26 | 48.90% | 21.66% | +27.24 |
| 32 | 09/02/26 | 48.92% | 0.30% ⚠️ | +48.62 |
| 33 | 09/03/26 | 49.03% | 0.30% ⚠️ | +48.73 |
| 34 | 09/04/26 | 49.21% | 21.62% | +27.59 |
| 35 | 09/05/26 | 49.08% | 21.62% | +27.46 |
| 36 | 09/06/26 | 49.26% | 21.62% | +27.64 |
| 37 | 09/07/26 | 50.56% | 21.65% | +28.91 |
| 38 | 09/08/26 | 50.46% | 0.23% ⚠️ | +50.23 |
| 39 | 09/09/26 | 50.33% | 0.23% ⚠️ | +50.10 |
| 40 | 09/10/26 | 50.22% | 0.23% ⚠️ | +49.99 |
| 41 | 09/11/26 | 50.09% | 0.23% ⚠️ | +49.85 |
| 42 | 09/12/26 | 49.81% | 0.23% ⚠️ | +49.58 |
| 43 | 09/13/26 | 49.65% | 0.23% ⚠️ | +49.42 |
| 44 | 09/14/26 | 49.56% | 21.65% | +27.91 |
| 45 | 09/15/26 | 49.52% | 21.65% | +27.87 |
| 46 | 09/16/26 | 49.52% | 21.65% | +27.87 |
| 47 | 09/17/26 | 49.46% | 21.65% | +27.81 |
| 48 | 09/18/26 | 49.32% | 21.65% | +27.67 |
| 49 | 09/19/26 | 49.13% | 21.65% | +27.48 |
| 50 | 09/20/26 | 49.02% | 21.65% | +27.37 |

Placer barely moved after the 9/8 lap (50.46 → 49.02). Compare Second Measure, which fell to 45.97. Possible reasons: different brand coverage, or the in-store-only channel. `INFERRED`, worth checking.

⚠️ = consensus history glitch (−5.24%, 0.30%, 0.23% on scattered days). It inflates the Diff on those days, so ignore Diff there.

---

## 5. Monthly trend — August 2026 (`DISCLOSED`)

| Source | Data Type | Metric | DKS YoY | Industry YoY | DKS − Ind (`DERIVED`) |
|---|---|---|---|---|---|
| Second Measure | US Transactions | Transaction Spend | +22.3% | -11.7% | +34.0 |
| Facteus | US Transactions | Transaction Spend | +2.3% | -16.5% | +18.8 |
| Placer.ai | US Foot Traffic | Foot Traffic Visits | +1.1% | -6.0% | +7.1 |
| Apptopia | Global Mobile App | App Time Spent | +52.4% | +11.9% | +40.5 |
| Similarweb | Global Web Traffic | Web Traffic Visits | +149.3% | +8.7% | +140.6 |

Industry = Sporting Goods Stores. **Second Measure (+22.3) vs Facteus (+2.3) disagree by 20pt on August.** Raw monthly numbers also don't line up with the adjusted QTD numbers (~46–52%). Don't mix adjusted and raw figures.

**Drivers (monthly YoY as of 08/31, `DISCLOSED`):**

| Driver | Component | YoY |
|---|---|---|
| BSM Transaction Spend | Avg Ticket | +3.5% |
| | Transaction Count | +18.2% |
| Apptopia App Time | iOS | +65.9% |
| | Android | +2.9% |
| Apptopia App Time | Dick's Sporting Goods app | +23.6% |
| | GameChanger app | −9.6% |

Check: 1.182 × 1.035 − 1 = 22.3%, which matches the 22.3% spend figure. Growth is volume-driven, not ticket-driven. `DERIVED`

---

## 6. Inflection — weekly Transaction Spend YoY (%) vs Retail–Discretionary (`DISCLOSED`)

Settings: Metric = Transaction Spend · Comp Source = Retail – Discretionary · Growth = YoY · Periodicity = Weekly · Range = 1Y (Second Measure). Peers without the metric and parents with same-industry subsidiaries are removed by Bloomberg.

### 6a. Latest 3 weeks + Bloomberg 3W trend

| Group | 13-Sep | 20-Sep | 27-Sep | 3W Avg (`DERIVED`) | BBG 3W Trend |
|---|---|---|---|---|---|
| Retail – Discretionary (aggregate) | -1.6 | -3.5 | -4.9 | -3.3 | ▼ Declining |
| Dick's Sporting Goods | -3.3 | -2.4 | -3.3 | -3.0 | — Mixed |
| Sporting Goods Stores | -17.0 | +2.6 | -10.6 | -8.3 | — Mixed |
| Automotive Retailers | -1.9 | +2.2 | +0.5 | +0.3 | — Mixed |
| Catalog & TV Based Retailers | -1.7 | -5.2 | -5.1 | -4.0 | — Mixed |
| Department Stores | -3.5 | -1.4 | +2.8 | -0.7 | ▲ Improving |
| Electronics & Appliance | +7.0 | +0.9 | -3.3 | +1.5 | ▼ Declining |
| Home Products Stores | +0.9 | -7.6 | -1.7 | -2.8 | — Mixed |
| Jewelry & Watch Stores | -12.0 | -4.3 | -11.6 | -9.3 | — Mixed |
| Other Spec Retail – Discretionary | +0.5 | -7.4 | -10.8 | -5.9 | ▼ Declining |
| Specialty Apparel Stores | -2.2 | -4.1 | -4.9 | -3.7 | ▼ Declining |

### 6b. Average weekly YoY by fiscal quarter (`DERIVED`)

Simple average of weekly YoY. It isn't dollar-weighted, so it won't equal the true quarterly YoY. Weeks are assigned to the quarter that holds most of their days (BBG weeks end Sunday; DKS quarters end Saturday).

| Group | 2026 Q3 | 2026 Q4 | 2027 Q1 | 2027 Q2 | 2027 Q3 (QTD) |
|---|---|---|---|---|---|
| *# weeks* | 5 (partial) | 13 | 13 | 13 | 8 |
| Retail – Discretionary (aggregate) | +0.7 | -0.5 | +1.1 | -0.5 | -1.7 |
| Dick's Sporting Goods | +30.5 | +27.3 | +31.8 | +22.2 | +13.3 |
| Sporting Goods Stores | +1.3 | +4.1 | -2.1 | -0.6 | -6.5 |
| Automotive Retailers | +0.6 | +4.6 | +7.4 | +4.8 | +3.2 |
| Catalog & TV Based Retailers | -8.4 | -11.2 | -9.5 | -7.6 | -12.0 |
| Department Stores | +0.3 | -1.9 | -1.9 | -0.4 | -1.4 |
| Electronics & Appliance | +3.0 | -4.4 | +6.4 | +4.6 | +0.0 |
| Home Products Stores | -0.3 | -2.6 | +0.8 | -1.4 | -1.3 |
| Jewelry & Watch Stores | -7.7 | -5.4 | -4.5 | -2.2 | -3.9 |
| Other Spec Retail – Discretionary | +0.0 | -1.9 | -0.9 | -1.8 | -2.5 |
| Specialty Apparel Stores | +2.8 | +0.7 | +2.2 | -1.0 | -3.6 |

**2027 Q3 split (DKS):** pre-lap weeks (09-Aug → 06-Sep, 5 wks) avg **+23.0** · post-lap weeks (13-Sep → 27-Sep, 3 wks) avg **-3.0**. `DERIVED`

### 6c. DKS spread vs peers (pp, `DERIVED`)

| Week ending | Fiscal Qtr | DKS | Sporting Goods | Retail-Disc | DKS − SG | DKS − RD |
|---|---|---|---|---|---|---|
| 05-Oct-25 | 2026 Q3 | +32.1 | +1.6 | +0.8 | +30.5 | +31.3 |
| 12-Oct-25 | 2026 Q3 | +30.1 | +2.2 | +1.3 | +27.9 | +28.8 |
| 19-Oct-25 | 2026 Q3 | +23.6 | -7.7 | -1.3 | +31.3 | +24.9 |
| 26-Oct-25 | 2026 Q3 | +36.4 | +2.9 | +2.5 | +33.5 | +33.9 |
| 02-Nov-25 | 2026 Q3 | +30.4 | +7.6 | +0.0 | +22.8 | +30.4 |
| 09-Nov-25 | 2026 Q4 | +42.3 | -1.8 | +3.0 | +44.1 | +39.3 |
| 16-Nov-25 | 2026 Q4 | +30.1 | +1.8 | -0.1 | +28.3 | +30.2 |
| 23-Nov-25 | 2026 Q4 | +27.4 | -1.6 | -1.6 | +29.0 | +29.0 |
| 30-Nov-25 | 2026 Q4 | +26.1 | -14.1 | -2.9 | +40.2 | +29.0 |
| 07-Dec-25 | 2026 Q4 | +19.1 | +9.9 | -3.6 | +9.2 | +22.7 |
| 14-Dec-25 | 2026 Q4 | +18.7 | +0.3 | -3.5 | +18.4 | +22.2 |
| 21-Dec-25 | 2026 Q4 | +16.8 | +0.6 | -0.5 | +16.2 | +17.3 |
| 28-Dec-25 | 2026 Q4 | +57.0 | +27.8 | +8.3 | +29.2 | +48.7 |
| 04-Jan-26 | 2026 Q4 | +36.0 | +17.1 | +2.8 | +18.9 | +33.2 |
| 11-Jan-26 | 2026 Q4 | +25.4 | +9.1 | +7.4 | +16.3 | +18.0 |
| 18-Jan-26 | 2026 Q4 | +24.3 | +2.1 | -2.4 | +22.2 | +26.7 |
| 25-Jan-26 | 2026 Q4 | +15.6 | +2.1 | -7.2 | +13.5 | +22.8 |
| 01-Feb-26 | 2026 Q4 | +15.5 | +0.5 | -6.5 | +15.0 | +22.0 |
| 08-Feb-26 | 2027 Q1 | +26.1 | +2.4 | +1.2 | +23.7 | +24.9 |
| 15-Feb-26 | 2027 Q1 | +41.0 | +6.5 | +5.5 | +34.5 | +35.5 |
| 22-Feb-26 | 2027 Q1 | +37.5 | -10.7 | +2.6 | +48.2 | +34.9 |
| 01-Mar-26 | 2027 Q1 | +43.7 | +4.3 | -0.9 | +39.4 | +44.6 |
| 08-Mar-26 | 2027 Q1 | +28.1 | -2.3 | +1.9 | +30.4 | +26.2 |
| 15-Mar-26 | 2027 Q1 | +31.7 | -6.0 | +0.1 | +37.7 | +31.6 |
| 22-Mar-26 | 2027 Q1 | +30.7 | -1.9 | -1.0 | +32.6 | +31.7 |
| 29-Mar-26 | 2027 Q1 | +29.5 | -12.5 | +2.5 | +42.0 | +27.0 |
| 05-Apr-26 | 2027 Q1 | +26.8 | -10.1 | -0.5 | +36.9 | +27.3 |
| 12-Apr-26 | 2027 Q1 | +31.4 | +7.6 | +2.3 | +23.8 | +29.1 |
| 19-Apr-26 | 2027 Q1 | +37.7 | -1.7 | +4.4 | +39.4 | +33.3 |
| 26-Apr-26 | 2027 Q1 | +24.6 | -5.3 | -2.4 | +29.9 | +27.0 |
| 03-May-26 | 2027 Q1 | +24.4 | +2.8 | -1.2 | +21.6 | +25.6 |
| 10-May-26 | 2027 Q2 | +21.1 | -4.2 | -0.9 | +25.3 | +22.0 |
| 17-May-26 | 2027 Q2 | +19.5 | +4.6 | -0.8 | +14.9 | +20.3 |
| 24-May-26 | 2027 Q2 | +22.2 | -3.1 | +0.3 | +25.3 | +21.9 |
| 31-May-26 | 2027 Q2 | +22.4 | +2.9 | +1.6 | +19.5 | +20.8 |
| 07-Jun-26 | 2027 Q2 | +18.9 | -4.9 | -0.9 | +23.8 | +19.8 |
| 14-Jun-26 | 2027 Q2 | +2.5 | -25.4 | -1.7 | +27.9 | +4.2 |
| 21-Jun-26 | 2027 Q2 | +58.4 | +29.4 | +4.8 | +29.0 | +53.6 |
| 28-Jun-26 | 2027 Q2 | +18.4 | +0.7 | -1.6 | +17.7 | +20.0 |
| 05-Jul-26 | 2027 Q2 | +20.0 | +1.6 | -3.7 | +18.4 | +23.7 |
| 12-Jul-26 | 2027 Q2 | +18.6 | +5.5 | +0.0 | +13.1 | +18.6 |
| 19-Jul-26 | 2027 Q2 | +19.8 | -9.0 | -2.0 | +28.8 | +21.8 |
| 26-Jul-26 | 2027 Q2 | +22.4 | -7.9 | -0.9 | +30.3 | +23.3 |
| 02-Aug-26 | 2027 Q2 | +24.8 | +2.4 | -0.2 | +22.4 | +25.0 |
| 09-Aug-26 | 2027 Q3 (QTD) | +27.5 | -1.1 | +2.1 | +28.6 | +25.4 |
| 16-Aug-26 | 2027 Q3 (QTD) | +20.1 | -4.9 | -0.3 | +25.0 | +20.4 |
| 23-Aug-26 | 2027 Q3 (QTD) | +20.7 | -10.7 | -0.6 | +31.4 | +21.3 |
| 30-Aug-26 | 2027 Q3 (QTD) | +29.0 | -13.4 | -5.8 | +42.4 | +34.8 |
| 06-Sep-26 | 2027 Q3 (QTD) | +17.9 | +3.4 | +0.7 | +14.5 | +17.2 |
| 13-Sep-26 | 2027 Q3 (QTD) | -3.3 | -17.0 | -1.6 | +13.7 | -1.7 |
| 20-Sep-26 | 2027 Q3 (QTD) | -2.4 | +2.6 | -3.5 | -5.0 | +1.1 |
| 27-Sep-26 | 2027 Q3 (QTD) | -3.3 | -10.6 | -4.9 | +7.3 | +1.6 |

### 6d. Full weekly table — all groups

| Week ending | Retail-Disc | DKS | Sporting Goods | Auto | Catalog/TV | Dept | Electronics | Home | Jewelry | Other Spec | Spec Apparel |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 05-Oct-25 | +0.8 | +32.1 | +1.6 | +0.6 | -9.6 | +5.3 | -16.2 | +2.2 | -20.2 | +0.5 | +1.7 |
| 12-Oct-25 | +1.3 | +30.1 | +2.2 | +3.1 | -4.5 | -2.0 | +9.4 | -2.4 | +29.5 | +2.4 | +3.0 |
| 19-Oct-25 | -1.3 | +23.6 | -7.7 | -3.9 | -14.8 | -0.2 | -2.0 | -0.8 | -16.8 | +0.2 | -0.3 |
| 26-Oct-25 | +2.5 | +36.4 | +2.9 | +2.4 | +4.9 | +0.4 | +35.0 | +1.4 | -8.9 | +1.6 | +4.8 |
| 02-Nov-25 | +0.0 | +30.4 | +7.6 | +0.7 | -18.2 | -2.1 | -11.2 | -2.0 | -22.3 | -4.5 | +4.7 |
| 09-Nov-25 | +3.0 | +42.3 | -1.8 | +4.3 | +0.1 | +0.2 | +11.8 | +4.2 | -14.4 | +1.1 | +6.5 |
| 16-Nov-25 | -0.1 | +30.1 | +1.8 | +8.6 | -15.2 | +0.9 | -29.3 | -0.6 | -18.6 | -2.1 | -0.2 |
| 23-Nov-25 | -1.6 | +27.4 | -1.6 | -1.4 | -9.7 | +0.4 | -9.7 | -2.5 | +1.8 | -1.6 | +0.1 |
| 30-Nov-25 | -2.9 | +26.1 | -14.1 | -0.2 | -17.9 | -0.1 | -2.5 | -4.4 | -13.3 | -4.4 | -0.4 |
| 07-Dec-25 | -3.6 | +19.1 | +9.9 | +1.5 | -8.7 | -4.2 | -11.8 | -6.1 | +1.1 | -4.8 | -2.7 |
| 14-Dec-25 | -3.5 | +18.7 | +0.3 | +4.9 | -11.6 | -6.5 | -31.4 | -7.1 | -21.4 | -4.5 | -1.4 |
| 21-Dec-25 | -0.5 | +16.8 | +0.6 | +6.1 | -2.9 | -7.1 | -5.3 | +1.3 | -2.6 | -2.9 | +0.1 |
| 28-Dec-25 | +8.3 | +57.0 | +27.8 | +8.5 | -19.7 | +14.8 | +4.4 | -2.3 | +8.3 | +3.9 | +12.8 |
| 04-Jan-26 | +2.8 | +36.0 | +17.1 | +1.4 | -5.9 | +4.2 | +9.4 | -9.2 | -5.7 | +1.3 | +9.1 |
| 11-Jan-26 | +7.4 | +25.4 | +9.1 | +21.3 | -15.6 | +4.9 | +9.1 | +0.9 | +7.5 | +7.3 | +6.1 |
| 18-Jan-26 | -2.4 | +24.3 | +2.1 | +1.3 | -15.3 | -9.0 | +10.6 | -2.6 | +16.4 | -2.7 | -4.6 |
| 25-Jan-26 | -7.2 | +15.6 | +2.1 | +6.1 | -14.8 | -15.5 | -11.4 | +9.6 | -15.7 | -8.6 | -9.5 |
| 01-Feb-26 | -6.5 | +15.5 | +0.5 | -2.2 | -8.6 | -8.3 | -0.9 | -15.4 | -13.5 | -6.7 | -6.3 |
| 08-Feb-26 | +1.2 | +26.1 | +2.4 | +10.4 | -8.1 | -4.6 | -15.3 | -1.5 | -21.7 | +0.1 | +2.8 |
| 15-Feb-26 | +5.5 | +41.0 | +6.5 | +16.0 | -10.9 | +0.7 | -1.0 | +8.0 | -7.4 | +2.1 | +8.3 |
| 22-Feb-26 | +2.6 | +37.5 | -10.7 | +14.4 | -10.8 | -7.7 | +0.0 | +3.6 | -14.5 | -0.2 | +5.3 |
| 01-Mar-26 | -0.9 | +43.7 | +4.3 | +0.6 | -10.2 | -1.5 | +88.7 | -1.9 | -22.3 | -5.5 | +2.1 |
| 08-Mar-26 | +1.9 | +28.1 | -2.3 | +7.4 | -4.0 | +2.9 | +1.3 | +4.9 | -12.2 | -3.6 | +2.0 |
| 15-Mar-26 | +0.1 | +31.7 | -6.0 | +4.8 | -7.6 | -4.0 | -8.0 | +0.1 | -18.5 | +0.5 | +1.5 |
| 22-Mar-26 | -1.0 | +30.7 | -1.9 | +7.8 | -4.7 | -2.4 | -19.9 | -3.1 | -11.2 | -3.8 | +0.7 |
| 29-Mar-26 | +2.5 | +29.5 | -12.5 | +8.4 | -8.8 | +5.4 | +11.6 | +2.3 | +6.4 | +2.7 | +2.4 |
| 05-Apr-26 | -0.5 | +26.8 | -10.1 | +4.7 | -17.0 | +6.1 | -22.6 | -4.4 | -10.5 | -3.9 | +5.0 |
| 12-Apr-26 | +2.3 | +31.4 | +7.6 | +5.9 | -6.2 | +2.6 | -12.8 | -3.4 | +0.6 | -4.0 | +5.8 |
| 19-Apr-26 | +4.4 | +37.7 | -1.7 | +9.5 | -8.8 | -9.3 | +32.4 | +8.8 | +1.3 | +6.7 | +0.1 |
| 26-Apr-26 | -2.4 | +24.6 | -5.3 | +2.3 | -12.8 | -8.7 | +0.2 | -1.0 | +8.2 | -1.9 | -3.3 |
| 03-May-26 | -1.2 | +24.4 | +2.8 | +3.8 | -13.5 | -4.7 | +29.2 | -2.6 | +43.5 | -0.3 | -3.6 |
| 10-May-26 | -0.9 | +21.1 | -4.2 | +4.4 | -7.9 | +0.1 | -10.5 | +2.2 | -0.7 | -0.5 | -3.0 |
| 17-May-26 | -0.8 | +19.5 | +4.6 | +3.3 | -7.9 | -6.3 | -8.0 | -0.4 | +3.0 | -0.5 | -3.7 |
| 24-May-26 | +0.3 | +22.2 | -3.1 | +5.6 | -7.4 | +7.7 | +39.1 | -3.8 | -2.8 | -0.9 | +0.7 |
| 31-May-26 | +1.6 | +22.4 | +2.9 | +6.9 | -6.0 | +2.8 | -18.0 | +3.1 | +9.5 | +0.2 | -0.8 |
| 07-Jun-26 | -0.9 | +18.9 | -4.9 | +9.3 | +0.3 | +0.0 | -2.5 | -2.3 | -5.0 | -3.1 | -3.6 |
| 14-Jun-26 | -1.7 | +2.5 | -25.4 | +5.4 | -8.0 | -7.6 | +2.1 | +1.5 | -10.7 | -2.4 | -2.2 |
| 21-Jun-26 | +4.8 | +58.4 | +29.4 | +6.5 | -5.5 | +10.0 | +40.0 | +0.5 | +12.1 | -1.3 | +6.7 |
| 28-Jun-26 | -1.6 | +18.4 | +0.7 | -0.8 | -24.4 | -0.8 | +13.2 | -1.5 | -11.8 | -4.6 | -1.5 |
| 05-Jul-26 | -3.7 | +20.0 | +1.6 | +5.2 | -9.0 | -1.5 | +6.1 | -11.4 | -14.4 | -5.7 | -4.3 |
| 12-Jul-26 | +0.0 | +18.6 | +5.5 | +4.6 | -13.7 | -4.3 | -18.1 | +1.2 | -5.3 | -0.5 | +1.7 |
| 19-Jul-26 | -2.0 | +19.8 | -9.0 | +2.8 | +9.5 | -6.7 | +8.5 | -1.1 | -11.7 | -2.7 | -1.1 |
| 26-Jul-26 | -0.9 | +22.4 | -7.9 | +5.1 | -8.9 | +0.0 | +13.5 | -4.6 | -11.1 | -0.2 | -1.0 |
| 02-Aug-26 | -0.2 | +24.8 | +2.4 | +4.5 | -9.3 | +1.6 | -5.1 | -1.4 | +20.4 | -1.0 | -0.9 |
| 09-Aug-26 | +2.1 | +27.5 | -1.1 | +5.7 | -22.0 | +10.8 | -1.5 | +2.0 | +11.8 | -1.3 | +1.2 |
| 16-Aug-26 | -0.3 | +20.1 | -4.9 | +6.4 | -18.4 | -5.8 | -19.7 | +4.0 | -12.1 | +1.2 | -3.2 |
| 23-Aug-26 | -0.6 | +20.7 | -10.7 | +2.5 | -24.5 | -0.6 | +8.8 | +1.6 | -5.8 | +0.4 | -3.7 |
| 30-Aug-26 | -5.8 | +29.0 | -13.4 | -0.3 | -13.0 | -7.5 | -7.7 | -10.0 | -4.4 | -3.7 | -7.8 |
| 06-Sep-26 | +0.7 | +17.9 | +3.4 | +10.2 | -6.2 | -5.7 | +15.1 | +0.1 | +7.0 | +0.8 | -3.8 |
| 13-Sep-26 | -1.6 | -3.3 | -17.0 | -1.9 | -1.7 | -3.5 | +7.0 | +0.9 | -12.0 | +0.5 | -2.2 |
| 20-Sep-26 | -3.5 | -2.4 | +2.6 | +2.2 | -5.2 | -1.4 | +0.9 | -7.6 | -4.3 | -7.4 | -4.1 |
| 27-Sep-26 | -4.9 | -3.3 | -10.6 | +0.5 | -5.1 | +2.8 | -3.3 | -1.7 | -11.6 | -10.8 | -4.9 |

Column key: **Retail-Disc** = Retail – Discretionary (aggregate) · **DKS** = Dick's Sporting Goods · **Sporting Goods** = Sporting Goods Stores · **Auto** = Automotive Retailers · **Catalog/TV** = Catalog & TV Based Retailers · **Dept** = Department Stores · **Electronics** = Electronics & Appliance · **Home** = Home Products Stores · **Jewelry** = Jewelry & Watch Stores · **Other Spec** = Other Spec Retail – Discretionary · **Spec Apparel** = Specialty Apparel Stores

---

## 7. Anomalies & data-quality flags

| Week / item | What | Read |
|---|---|---|
| w/e 28-Dec-25 | DKS +57.0, SG +27.8, Retail-Disc +8.3. Spike across every category | Holiday/calendar alignment, not DKS-specific. `INFERRED` |
| w/e 14-Jun / 21-Jun-26 | SG −25.4 → +29.4; DKS +2.5 → +58.4 | Father's Day shift (6/15/25 vs 6/21/26). Average the two weeks. `INFERRED` |
| w/e 01-Mar-26 | Electronics +88.7 | One-off outlier; ignore. |
| QTD consensus | −5.24 / 0.30 / 0.23% on scattered days | Glitch in consensus history; Diff is meaningless on those days. |
| BSM vs Facteus Aug | +22.3 vs +2.3 | Likely explained: Facteus shows only a small post-deal step-up, so it probably excludes FL banners (see §9b). `INFERRED` |
| Adj vs raw | QTD Adj ~46–52%; raw weekly/monthly ~18–29% pre-lap | Different bases. Keep them separate. |
| Brands = All Covered | Includes Foot Locker banners | Total-company spend vs DKS-only comps is a mismatch. |

---

## 8. Entitlements — Trend Analysis metric availability (`DISCLOSED`)

| Source | Available | Locked / unavailable |
|---|---|---|
| Second Measure | Spend, Count, Customers, Avg Ticket, Count/Customer, Spend/Customer | — |
| Facteus | Spend, Count, Avg Ticket | Customers |
| Placer.ai | Foot Traffic Visits | Same-Store Visits, Avg Dwell, Visit Frequency, Visitors |
| Apptopia | App Time Spent, Downloads | MAU, DAU, Sessions, Revenue |
| Similarweb | Web Traffic Visits | Visitors, Avg Visit Duration, Bounce Rate, Page Views |

---

## 9. Trend Analysis — Second Measure monthly KPIs, YoY % (Oct-23 → Aug-26)

**Source:** Trend Analysis tab, Monthly, YoY, 3Y. **Only Aug-26 is `DISCLOSED`** (bold row, from the chart legend). Every other month is `ESTIMATED`: digitized from the chart's pixels and calibrated to the Aug-26 values and the 0% line (calibration error ≤0.05pp).

**Accuracy check:** Spend should equal (1+Count)×(1+Ticket)−1. Across all 26 months where every line was visible, the digitized values satisfy this within ~0.1pp. Treat each value as **±0.2pp**.

† = that line was hidden behind another line on the chart, so I backed it out from the identity: Ticket = (1+Spend)/(1+Count)−1. In Feb-25 and Feb-26, Count was hidden under Customers, so I set Count = Customers.

| Month | Spend | Count | Customers | Avg Ticket | Spend / Customer | Count / Customer* |
|---|---|---|---|---|---|---|
| Oct-23 | -7.7 | -8.3 | -8.0 | +0.6† | +0.3 | 0.0 |
| Nov-23 | -3.9 | -4.0 | -4.6 | +0.2 | +0.8 | 0.0 |
| Dec-23 | -1.3 | -4.5 | -3.5 | +3.3† | +2.3 | 0.0 |
| Jan-24 | -1.1 | -4.0 | -5.1 | +3.1 | +4.2 | 0.0 |
| Feb-24 | +0.3 | +0.5 | -0.9 | -0.1 | +1.2 | 0.0 |
| Mar-24 | +5.7 | +3.4 | +2.9 | +2.2 | +2.7 | 0.0 |
| Apr-24 | -4.1 | -5.7 | -5.2 | +1.7 | +1.2 | 0.0 |
| May-24 | +1.1 | -0.4 | +1.3 | +1.5† | -0.2 | 0.0 |
| Jun-24 | +1.9 | +0.4 | +1.4 | +1.5† | +0.4 | 0.0 |
| Jul-24 | -7.3 | -9.4 | -7.7 | +2.2 | +0.4 | 0.0 |
| Aug-24 | +3.4 | -0.4 | +0.2 | +3.8 | +3.2 | 0.0 |
| Sep-24 | -7.1 | -8.4 | -7.7 | +1.3 | +0.5 | 0.0 |
| Oct-24 | -2.1 | -4.6 | -4.7 | +2.6† | +2.8 | 0.0 |
| Nov-24 | -4.3 | -6.8 | -6.0 | +2.6 | +1.8 | 0.0 |
| Dec-24 | +0.8 | -1.0 | -2.4 | +1.9 | +3.3 | 0.0 |
| Jan-25 | +0.5 | -2.3 | -3.1 | +2.9 | +3.6 | 0.0 |
| Feb-25 | -5.7 | -7.7† | -7.7 | +2.2† | +2.2 | 0.0 |
| Mar-25 | +1.1 | -1.8 | -2.2 | +3.1 | +3.5 | 0.0 |
| Apr-25 | -3.2 | -4.9 | -5.1 | +1.7 | +2.1 | 0.0 |
| May-25 | +3.7 | -2.0 | -2.7 | +5.8 | +6.5 | 0.0 |
| Jun-25 | -4.5 | -7.3 | -7.0 | +2.9 | +2.7 | 0.0 |
| Jul-25 | +6.2 | +0.4 | -0.2 | +5.8† | +6.5 | 0.0 |
| Aug-25 | +3.9 | -1.6 | -2.3 | +5.5 | +6.3 | 0.0 |
| Sep-25 | +16.6 | +9.3 | +10.1 | +6.5 | +5.8 | 0.0 |
| Oct-25 | +32.6 | +22.8 | +22.4 | +8.0 | +8.4 | 0.0 |
| Nov-25 | +32.8 | +23.8 | +23.1 | +7.3 | +7.9 | 0.0 |
| Dec-25 | +24.8 | +16.9 | +17.1 | +6.7 | +6.5 | 0.0 |
| Jan-26 | +26.1 | +16.7 | +17.9 | +8.1 | +7.0 | 0.0 |
| Feb-26 | +39.5 | +25.0† | +25.0 | +11.5† | +11.6 | 0.0 |
| Mar-26 | +26.1 | +18.1 | +17.3 | +6.9 | +7.6 | 0.0 |
| Apr-26 | +30.4 | +23.0 | +22.2 | +6.0 | +6.7 | 0.0 |
| May-26 | +22.6 | +18.2 | +17.9 | +3.8 | +4.0 | 0.0 |
| Jun-26 | +21.8 | +17.6 | +17.1 | +3.7 | +4.0 | 0.0 |
| Jul-26 | +23.6 | +19.8 | +18.8 | +3.1† | +4.1 | 0.0 |
| **Aug-26** | **+22.27** | **+18.15** | **+17.77** | **+3.49** | **+3.83** | **0.00** |

\* Count/Customer is flat at 0.00 every month on Bloomberg. That can't be right: Count and Customers grow at different rates (e.g., Oct-25 implies about +0.3%), so the series looks unpopulated. Don't use it.

### Averages: pre-deal vs post-deal (`DERIVED` from estimates)

| Period | Months | Spend | Count | Customers | Avg Ticket | Spend / Cust |
|---|---|---|---|---|---|---|
| Pre-deal (Oct-23 → Aug-25) | 23 | -1.0 | -3.5 | -3.5 | +2.5 | +2.5 |
| Sep-25 (deal closed 9/8) | 1 | +16.6 | +9.3 | +10.1 | +6.5 | +5.8 |
| Post-deal (Oct-25 → Aug-26) | 11 | +27.5 | +20.0 | +19.7 | +6.2 | +6.5 |

### Reads

1. **Before the deal, growth came from ticket while transactions shrank.** Count averaged -3.5% and ticket +2.5%. Spend was roughly flat. `DERIVED`
2. **After the deal, the jump is customers.** Customers averaged +19.7% and count +20.0%. That's consistent with Foot Locker shoppers entering the panel. `INFERRED`
3. **Ticket and spend-per-customer are decelerating.** Ticket peaked at about +11.5% (Feb-26) and has fallen to +3.5% (Aug-26). The deal affects it less than count or customers (though Foot Locker's mix can still move it), so it's the cleaner read on the underlying business. `DERIVED` / `INFERRED`
4. **Expect Spend YoY to fall sharply from Sep-26 as customers and count lap.** The weekly Inflection data already shows this (−3.0% average post-lap, section 6). `INFERRED`

---

## 9b. Trend Analysis — Facteus monthly KPIs, YoY % (Nov-23 → Aug-26)

**Source:** Trend Analysis, Facteus Arbiter, Monthly, YoY, 3Y. **Aug-26 is `DISCLOSED`** (from the legend). All other months are `ESTIMATED`, digitized from chart pixels. This chart's scale is finer than the Second Measure one (~24px per 1pp), so these estimates are tighter. Spend = (1+Count)(1+Ticket)−1 holds within 0.06pp in every month. Treat each value as **±0.1pp**. All three lines were visible every month, so no values had to be backed out.

| Month | Spend | Count | Avg Ticket | BSM Spend (§9) | BSM − Facteus |
|---|---|---|---|---|---|
| Nov-23 | -1.5 | -2.8 | +1.3 | -3.9 | -2.4 |
| Dec-23 | -2.1 | -4.2 | +2.3 | -1.3 | +0.8 |
| Jan-24 | -2.0 | -4.5 | +2.6 | -1.1 | +0.9 |
| Feb-24 | -4.8 | -4.2 | -0.6 | +0.3 | +5.1 |
| Mar-24 | +6.2 | +2.9 | +3.3 | +5.7 | -0.6 |
| Apr-24 | -4.6 | -6.1 | +1.6 | -4.1 | +0.5 |
| May-24 | -0.8 | -2.0 | +1.2 | +1.1 | +1.9 |
| Jun-24 | +1.4 | -0.6 | +2.0 | +1.9 | +0.6 |
| Jul-24 | -3.0 | -6.1 | +3.3 | -7.3 | -4.4 |
| Aug-24 | +4.5 | +0.2 | +4.3 | +3.4 | -1.1 |
| Sep-24 | -6.1 | -7.4 | +1.5 | -7.1 | -1.1 |
| Oct-24 | -8.1 | -8.9 | +0.9 | -2.1 | +6.0 |
| Nov-24 | -8.2 | -9.8 | +1.7 | -4.3 | +3.9 |
| Dec-24 | -0.1 | -2.3 | +2.2 | +0.8 | +1.0 |
| Jan-25 | -2.3 | -2.1 | -0.2 | +0.5 | +2.8 |
| Feb-25 | -5.9 | -8.0 | +2.4 | -5.7 | +0.2 |
| Mar-25 | -0.8 | -2.8 | +2.0 | +1.1 | +2.0 |
| Apr-25 | -4.9 | -7.0 | +2.2 | -3.2 | +1.8 |
| May-25 | -0.5 | -3.7 | +3.3 | +3.7 | +4.3 |
| Jun-25 | -5.2 | -7.9 | +2.9 | -4.5 | +0.7 |
| Jul-25 | -1.3 | -4.3 | +3.1 | +6.2 | +7.6 |
| Aug-25 | -0.8 | -4.9 | +4.3 | +3.9 | +4.7 |
| Sep-25 | +0.1 | -2.5 | +2.7 | +16.6 | +16.4 |
| Oct-25 | +14.2 | +8.4 | +5.4 | +32.6 | +18.4 |
| Nov-25 | +11.7 | +6.9 | +4.6 | +32.8 | +21.0 |
| Dec-25 | +5.1 | +1.4 | +3.7 | +24.8 | +19.7 |
| Jan-26 | +4.9 | -0.1 | +5.0 | +26.1 | +21.2 |
| Feb-26 | +13.3 | +6.7 | +6.1 | +39.5 | +26.2 |
| Mar-26 | +3.2 | -1.0 | +4.3 | +26.1 | +22.9 |
| Apr-26 | +8.4 | +5.5 | +2.8 | +30.4 | +21.9 |
| May-26 | +6.1 | +2.2 | +3.8 | +22.6 | +16.5 |
| Jun-26 | +3.1 | -0.2 | +3.3 | +21.8 | +18.7 |
| Jul-26 | +3.5 | +0.5 | +3.0 | +23.6 | +20.1 |
| **Aug-26** | **+2.28** | **−0.06** | **+2.34** | **+22.27** | **+20.0** |

### Pre-deal vs post-deal averages (`DERIVED`)

| Period | Months | Facteus Spend | Facteus Count | Facteus Ticket | BSM Spend | Gap (BSM − Facteus) |
|---|---|---|---|---|---|---|
| Pre-deal (Nov-23 → Aug-25) | 22 | -2.3 | -4.4 | +2.2 | -0.7 | +1.6 |
| Post-deal (Oct-25 → Aug-26) | 11 | +6.9 | +2.7 | +4.0 | +27.5 | +20.6 |

### Reads

1. **Facteus barely reacts to the deal.** Second Measure jumps ~28pt after the deal; Facteus moves only ~9pt. Facteus most likely doesn't capture Foot Locker banners. That would explain the 20pt August gap flagged in section 7. `INFERRED`
2. **If that's right, Facteus is close to an organic DKS read.** Post-deal: spend +6.9%, count +2.7%, ticket +4.0%. The latest month (Aug-26) is spend +2.3%, flat count, ticket +2.3%. `INFERRED`
3. **The BSM − Facteus gap is a rough measure of Foot Locker's contribution.** Pre-deal the two sources were within ~1.6pt of each other; post-deal the gap averages ~21pt. The two panels cover different merchants and cardholders, so this is a rough estimate. `INFERRED`
4. **Test it:** compare Facteus quarterly averages to DKS-segment comps in the 10-Qs. If they track, Facteus can serve as the organic proxy. Check also whether Oct-25, Nov-25 and Feb-26 (+12 to +14) reflect partial Foot Locker coverage or real DKS strength.

## 9c. Second Measure weekly — latest week snapshot (`DISCLOSED`)

From the Trend Analysis legend, Weekly, w/e 27-Sep-26 (the third week after the lap). The weekly chart itself is too dense and noisy from holiday shifts to digitize.

| Metric | YoY |
|---|---|
| Spend | −3.33 |
| Count | −4.45 |
| Customers | −5.86 |
| Avg Ticket | +1.17 |
| Spend / Customer | +2.68 |

Post-lap, transactions are down 4.5% and ticket is only +1.2%, compared with +3.5% ticket in August (monthly). `DERIVED`

---

## 9d. Placer, Apptopia, Similarweb — MONTHLY, YoY % (Oct-23 → Aug-26)

**Source:** Trend Analysis, **Monthly**, YoY, 3Y. **Aug-26 is `DISCLOSED`** (bold row, from each legend). All other months are `ESTIMATED`, digitized from chart pixels. Approximate accuracy by chart scale: Placer ±0.2pp; Apptopia ±0.5pp; Similarweb ±1pp. BSM and Facteus Spend columns are repeated from §9 and §9b for side-by-side comparison.

| Month | Placer Foot Traffic | Apptopia App Time | Apptopia Downloads | Similarweb Web Visits | BSM Spend | Facteus Spend |
|---|---|---|---|---|---|---|
| Oct-23 | -5.5 | +36 | +11 | +18 | -7.7 | — |
| Nov-23 | -2.2 | +49 | +25 | +15 | -3.9 | -1.5 |
| Dec-23 | -0.5 | +73 | +61 | +6 | -1.3 | -2.1 |
| Jan-24 | -8.7 | +45 | +24 | +7 | -1.1 | -2.0 |
| Feb-24 | 0.0 | +37 | +15 | +3 | +0.3 | -4.8 |
| Mar-24 | +1.9 | +19 | -5 | -2 | +5.7 | +6.2 |
| Apr-24 | -7.9 | +21 | +6 | -2 | -4.1 | -4.6 |
| May-24 | +1.3 | +20 | +1 | -6 | +1.1 | -0.8 |
| Jun-24 | +3.0 | +27 | +12 | -4 | +1.9 | +1.4 |
| Jul-24 | -6.0 | +25 | +15 | -12 | -7.3 | -3.0 |
| Aug-24 | +1.4 | +29 | +11 | -10 | +3.4 | +4.5 |
| Sep-24 | -8.6 | +16 | -12 | -13 | -7.1 | -6.1 |
| Oct-24 | -9.5 | +16 | -1 | -23 | -2.1 | -8.1 |
| Nov-24 | -4.2 | +19 | -15 | -23 | -4.3 | -8.2 |
| Dec-24 | -7.6 | +17 | -5 | -11 | +0.8 | -0.1 |
| Jan-25 | -3.6 | +22 | +12 | -17 | +0.5 | -2.3 |
| Feb-25 | -13.3 | +27 | +3 | -15 | -5.7 | -5.9 |
| Mar-25 | -2.4 | +26 | -1 | -7 | +1.1 | -0.8 |
| Apr-25 | -5.9 | +18 | -6 | -18 | -3.2 | -4.9 |
| May-25 | -1.7 | +20 | 0 | -12 | +3.7 | -0.5 |
| Jun-25 | -9.4 | +21 | +5 | -14 | -4.5 | -5.2 |
| Jul-25 | -1.5 | +37 | +30 | -6 | +6.2 | -1.3 |
| Aug-25 | -1.5 | +28 | +6 | -3 | +3.9 | -0.8 |
| Sep-25 | -1.1 | +67 | +35 | +63 | +16.6 | +0.1 |
| Oct-25 | +11.6 | +88 | +57 | +133 | +32.6 | +14.2 |
| Nov-25 | +7.8 | +108 | +86 | +143 | +32.8 | +11.7 |
| Dec-25 | +1.5 | +100 | +64 | +125 | +24.8 | +5.1 |
| Jan-26 | +8.4 | +72 | +12 | +110 | +26.1 | +4.9 |
| Feb-26 | +10.5 | +90 | +76 | +112 | +39.5 | +13.3 |
| Mar-26 | -1.0 | +80 | +58 | +111 | +26.1 | +3.2 |
| Apr-26 | +7.2 | +67 | +44 | +144 | +30.4 | +8.4 |
| May-26 | +6.9 | +54 | +37 | +134 | +22.6 | +6.1 |
| Jun-26 | +7.9 | +46 | +22 | +141 | +21.8 | +3.1 |
| Jul-26 | +4.8 | +39 | +12 | +164 | +23.6 | +3.5 |
| **Aug-26** | **+1.14** | **+52.45** | **+47.15** | **+149.27** | **+22.27** | **+2.28** |

Facteus data starts Nov-23, so its Oct-23 cell is blank.

### All sources: pre-deal vs post-deal averages (`DERIVED`)

| Source | Pre-deal avg (→ Aug-25) | Post-deal avg (Oct-25 →) | Step-up (pp) | Aug-26 |
|---|---|---|---|---|
| BSM Spend | -1.0 | +27.5 | +28.5 | +22.27 |
| Facteus Spend | -2.3 | +6.9 | +9.2 | +2.28 |
| Placer Foot Traffic | -4.0 | +6.1 | +10.1 | +1.14 |
| Apptopia App Time | +28 | +73 | +44 | +52.45 |
| Apptopia Downloads | +8 | +47 | +38 | +47.15 |
| Similarweb Web Visits | -6 | +133 | +140 | +149.27 |

## 9e. Placer, Apptopia, Similarweb — WEEKLY, latest weeks

**Source:** Trend Analysis, **Weekly**, YoY, 3Y. The latest week is `DISCLOSED` (legend). Earlier weeks are `ESTIMATED`. Weekly charts are dense, so accuracy is lower than monthly: Placer ±0.5pp, Apptopia ±1–2pp, Similarweb ±1pp.

**Date assumption:** the last point is w/e 27-Sep-26. That matches the BSM weekly legend (−3.33) against the Inflection table (w/e 27-Sep: −3.3). Placer and Apptopia show 155 weekly points; Similarweb shows 156 (one extra week at the start).

| Week ending | Placer Foot Traffic | Apptopia App Time | Apptopia Downloads | Similarweb Web Visits | BSM Spend (Inflection, exact) |
|---|---|---|---|---|---|
| 05-Jul-26 | +9.3 | +63 | +45 | +154 | +20.0 |
| 12-Jul-26 | +5.6 | +36 | -5 | +168 | +18.6 |
| 19-Jul-26 | +4.9 | +24 | -14 | +162 | +19.8 |
| 26-Jul-26 | +2.3 | +47 | +27 | +167 | +22.4 |
| 02-Aug-26 | +2.6 | +51 | +38 | +158 | +24.8 |
| 09-Aug-26 | +0.8 | +50 | +42 | +165 | +27.5 |
| 16-Aug-26 | +6.9 | +53 | +47 | +143 | +20.1 |
| 23-Aug-26 | +0.4 | +53 | +45 | +135 | +20.7 |
| 30-Aug-26 | +0.7 | — | +55 | +155 | +29.0 |
| 06-Sep-26 | +3.8 | +49 | +39 | +147 | +17.9 |
| 13-Sep-26 | -4.4 | +55 | +53 | +33 | -3.3 |
| 20-Sep-26 | +4.8 | +13 | +31 | +43 | -2.4 |
| **27-Sep-26** | **−3.80** | **+24.55** | **+38.73** | **+35.24** | **−3.3** |

Shown: last 13 weeks, i.e. 2027 Q2 end plus 2027 Q3 to date. The full 3-year weekly series is in Appendix A.

### Reads

1. **Every source steps up after the Foot Locker deal, but by very different amounts.** Similarweb +140pp, Apptopia app time +44pp, BSM +29pp, Facteus +9pp, Placer +10pp. The size of the jump shows how much Foot Locker each panel captures. `DERIVED` / `INFERRED`
2. **Placer behaves like Facteus: a small step-up.** It likely captures few or no Foot Locker stores, so it's a second candidate for an organic DKS read. Aug-26 foot traffic was +1.1%. `INFERRED`
3. **The weekly data confirms the lap in mid-Sep-26.** Similarweb fell from ~149% (5 weeks to 06-Sep) to ~37% (last 3 weeks). BSM went from +18 to +29 down to −3. Placer went from ~+2.5% to ~-1.2%. `DERIVED`
4. **Similarweb is still +35% after the lap, and Apptopia +25–39%.** Digital engagement is growing much faster than spend. That's either real digital strength or panel/domain changes (e.g., site or app migrations). Neither source predicts revenue well (MAE 12–14pt, §2), so use them for timing, not size. `INFERRED`

---

## 10. Still to capture

- [ ] QTD Second Measure, days 37–57 (shows the post-lap decline day by day)
- [ ] KPI Correlation quarterly table: Facteus, Placer
- [ ] QTD Facteus daily build
- [ ] Brands filter: does it isolate DKS banners vs Foot Locker?
- [ ] Inflection set to 3Y (pre-acquisition baseline)
- [ ] Exact monthly values for section 9 (only via a working Excel/BQL connection; the chart only shows the latest month)

---

## Appendix A — Full weekly series, YoY % (`ESTIMATED` except last row)

Digitized from the weekly Trend Analysis charts. Dates assume the last point is w/e 27-Sep-26. Big swings around Thanksgiving, Christmas and Father's Day are holiday-calendar shifts, not demand. Accuracy: Placer ±0.5pp, Apptopia ±1–2pp, Similarweb ±1pp. — = line hidden behind another line, or no data.

| Week ending | Placer | App Time | App Downloads | Web Visits |
|---|---|---|---|---|
| 08-Oct-23 | — | — | — | +18 |
| 15-Oct-23 | -3.4 | +35 | +11 | +15 |
| 22-Oct-23 | +0.6 | +33 | -3 | +15 |
| 29-Oct-23 | -2.5 | +34 | +4 | +21 |
| 05-Nov-23 | -3.2 | +41 | +18 | +26 |
| 12-Nov-23 | +0.8 | +46 | +30 | +17 |
| 19-Nov-23 | -4.8 | +48 | +34 | +11 |
| 26-Nov-23 | -8.9 | +46 | +33 | +8 |
| 03-Dec-23 | +1.8 | +47 | +33 | +17 |
| 10-Dec-23 | -3.7 | +66 | +38 | +14 |
| 17-Dec-23 | -4.6 | +111 | +88 | +3 |
| 24-Dec-23 | -7.1 | +40 | +6 | +10 |
| 31-Dec-23 | +17.7 | +106 | +154 | -7 |
| 07-Jan-24 | -11.3 | +48 | +30 | -2 |
| 14-Jan-24 | -11.2 | +46 | +19 | +10 |
| 21-Jan-24 | -8.6 | +49 | +34 | +6 |
| 28-Jan-24 | -7.4 | +50 | +29 | +17 |
| 04-Feb-24 | -4.8 | +43 | +18 | +5 |
| 11-Feb-24 | -1.8 | +36 | +9 | +5 |
| 18-Feb-24 | -5.7 | +36 | +11 | +4 |
| 25-Feb-24 | -3.4 | +36 | +15 | -4 |
| 03-Mar-24 | -0.7 | +25 | 0 | -7 |
| 10-Mar-24 | -2.1 | +18 | -6 | -4 |
| 17-Mar-24 | +0.2 | +7 | -18 | +1 |
| 24-Mar-24 | +0.3 | +22 | +6 | +3 |
| 31-Mar-24 | -4.4 | +23 | +4 | -9 |
| 07-Apr-24 | -10.5 | +13 | -11 | -1 |
| 14-Apr-24 | +9.6 | +22 | +11 | -1 |
| 21-Apr-24 | -11.0 | +25 | +12 | -5 |
| 28-Apr-24 | -1.3 | +22 | +5 | +1 |
| 05-May-24 | -2.6 | +22 | +6 | +5 |
| 12-May-24 | +2.4 | +20 | -1 | -7 |
| 19-May-24 | +0.2 | +16 | -5 | -8 |
| 26-May-24 | -1.4 | +18 | 0 | -10 |
| 02-Jun-24 | -2.9 | +18 | -6 | -9 |
| 09-Jun-24 | -2.4 | +29 | +16 | -4 |
| 16-Jun-24 | +2.6 | +33 | +31 | -4 |
| 23-Jun-24 | +0.6 | +29 | +13 | -4 |
| 30-Jun-24 | +1.7 | +23 | +5 | -6 |
| 07-Jul-24 | +0.5 | +27 | +12 | -13 |
| 14-Jul-24 | -0.1 | +21 | -3 | -7 |
| 21-Jul-24 | -2.0 | +25 | +7 | -7 |
| 28-Jul-24 | -8.2 | +27 | +12 | -15 |
| 04-Aug-24 | -6.1 | +33 | +34 | -18 |
| 11-Aug-24 | -3.1 | +33 | +30 | -17 |
| 18-Aug-24 | -1.8 | +26 | +6 | -11 |
| 25-Aug-24 | -0.2 | +26 | +5 | -7 |
| 01-Sep-24 | +0.5 | +32 | +18 | -1 |
| 08-Sep-24 | -0.4 | +27 | +6 | -7 |
| 15-Sep-24 | -2.0 | +20 | -8 | -11 |
| 22-Sep-24 | -4.0 | +15 | -15 | -15 |
| 29-Sep-24 | -4.8 | +17 | -10 | -13 |
| 06-Oct-24 | -8.5 | +14 | -11 | -20 |
| 13-Oct-24 | -8.1 | +15 | -7 | -18 |
| 20-Oct-24 | -11.0 | +17 | +7 | -21 |
| 27-Oct-24 | -3.3 | +20 | +5 | -28 |
| 03-Nov-24 | -9.3 | +18 | +1 | -32 |
| 10-Nov-24 | -10.1 | +20 | +1 | -31 |
| 17-Nov-24 | -11.7 | +22 | +2 | -27 |
| 24-Nov-24 | -2.3 | +32 | +16 | -44 |
| 01-Dec-24 | -38.2 | +57 | +48 | +8 |
| 08-Dec-24 | +25.6 | -27 | -67 | -6 |
| 15-Dec-24 | -9.5 | +16 | +1 | -14 |
| 22-Dec-24 | -13.7 | +21 | +1 | -11 |
| 29-Dec-24 | -15.4 | +25 | +5 | -4 |
| 05-Jan-25 | +26.7 | +27 | +12 | -13 |
| 12-Jan-25 | +10.3 | +17 | -1 | -20 |
| 19-Jan-25 | -2.5 | +15 | -11 | -14 |
| 26-Jan-25 | -4.9 | +18 | +9 | -14 |
| 02-Feb-25 | -3.0 | +28 | +26 | -14 |
| 09-Feb-25 | -10.2 | +41 | +39 | -15 |
| 16-Feb-25 | -11.0 | +34 | +13 | -12 |
| 23-Feb-25 | -12.3 | +25 | -1 | -11 |
| 02-Mar-25 | -16.6 | +26 | -3 | -11 |
| 09-Mar-25 | -4.3 | +28 | -2 | -8 |
| 16-Mar-25 | -5.5 | +27 | -4 | -7 |
| 23-Mar-25 | -6.1 | +24 | -7 | -13 |
| 30-Mar-25 | +1.2 | +19 | -9 | +1 |
| 06-Apr-25 | +7.0 | +31 | +16 | -15 |
| 13-Apr-25 | -7.2 | +24 | +1 | -17 |
| 20-Apr-25 | -6.3 | +15 | -14 | -22 |
| 27-Apr-25 | -10.2 | +14 | -10 | -19 |
| 04-May-25 | +2.4 | +17 | -7 | -14 |
| 11-May-25 | -3.2 | +27 | +15 | -10 |
| 18-May-25 | -5.3 | +20 | -5 | -13 |
| 25-May-25 | -3.9 | +22 | +8 | -13 |
| 01-Jun-25 | -4.5 | +20 | -4 | -13 |
| 08-Jun-25 | -5.9 | +17 | -4 | -16 |
| 15-Jun-25 | -7.7 | +19 | -2 | -16 |
| 22-Jun-25 | -7.5 | +28 | +13 | -13 |
| 29-Jun-25 | -7.6 | +20 | 0 | -10 |
| 06-Jul-25 | -6.9 | +20 | +9 | -14 |
| 13-Jul-25 | -7.6 | +44 | +74 | -12 |
| 20-Jul-25 | -2.8 | +53 | +74 | -2 |
| 27-Jul-25 | +5.1 | +36 | +25 | +1 |
| 03-Aug-25 | -0.9 | +24 | -5 | +2 |
| 10-Aug-25 | -3.3 | +22 | -11 | -1 |
| 17-Aug-25 | -0.4 | +30 | +13 | +1 |
| 24-Aug-25 | -1.2 | +31 | +17 | -3 |
| 31-Aug-25 | -2.5 | +22 | -4 | -13 |
| 07-Sep-25 | -4.4 | +29 | +11 | -6 |
| 14-Sep-25 | -6.0 | +27 | +7 | +83 |
| 21-Sep-25 | +3.3 | +74 | +36 | +93 |
| 28-Sep-25 | +5.6 | +78 | +43 | +92 |
| 05-Oct-25 | +6.8 | +93 | +66 | +108 |
| 12-Oct-25 | +8.0 | +92 | +63 | +128 |
| 19-Oct-25 | +8.8 | +92 | +63 | +125 |
| 26-Oct-25 | +7.3 | +84 | +60 | +158 |
| 02-Nov-25 | +15.3 | +86 | +44 | +138 |
| 09-Nov-25 | +9.7 | +91 | +56 | +157 |
| 16-Nov-25 | +12.6 | +90 | +55 | +142 |
| 23-Nov-25 | +11.4 | +104 | +72 | +148 |
| 30-Nov-25 | +5.4 | +106 | +94 | +120 |
| 07-Dec-25 | +1.3 | +135 | +121 | +118 |
| 14-Dec-25 | +2.0 | +88 | +42 | +122 |
| 21-Dec-25 | -2.7 | +130 | +105 | +139 |
| 28-Dec-25 | -5.9 | +86 | +45 | +135 |
| 04-Jan-26 | +13.4 | +102 | +78 | +124 |
| 11-Jan-26 | +12.6 | +98 | +68 | +118 |
| 18-Jan-26 | +11.9 | +78 | +29 | +100 |
| 25-Jan-26 | +4.1 | +75 | +14 | +111 |
| 01-Feb-26 | -2.0 | +66 | 0 | +104 |
| 08-Feb-26 | +3.9 | +51 | -13 | +105 |
| 15-Feb-26 | +8.5 | +67 | +48 | +104 |
| 22-Feb-26 | +13.6 | +72 | +50 | +110 |
| 01-Mar-26 | +8.3 | — | +100 | +122 |
| 08-Mar-26 | +3.2 | +138 | +134 | +114 |
| 15-Mar-26 | +4.2 | +93 | +62 | +108 |
| 22-Mar-26 | +0.7 | +73 | +41 | +115 |
| 29-Mar-26 | +1.8 | +68 | +44 | +109 |
| 05-Apr-26 | +5.1 | +70 | +48 | +128 |
| 12-Apr-26 | -2.1 | +76 | +61 | +128 |
| 19-Apr-26 | +17.6 | +62 | +30 | +158 |
| 26-Apr-26 | +15.5 | +68 | +49 | +152 |
| 03-May-26 | +1.4 | +74 | +65 | +154 |
| 10-May-26 | +4.0 | +52 | +29 | +149 |
| 17-May-26 | +6.2 | +59 | +53 | +130 |
| 24-May-26 | +5.5 | +56 | +39 | +122 |
| 31-May-26 | +5.7 | +60 | +59 | +118 |
| 07-Jun-26 | +4.5 | +44 | +15 | +128 |
| 14-Jun-26 | +6.1 | +40 | +11 | +131 |
| 21-Jun-26 | -2.0 | +33 | +9 | +159 |
| 28-Jun-26 | +26.2 | +58 | +45 | +151 |
| 05-Jul-26 | +9.3 | +63 | +45 | +154 |
| 12-Jul-26 | +5.6 | +36 | -5 | +168 |
| 19-Jul-26 | +4.9 | +24 | -14 | +162 |
| 26-Jul-26 | +2.3 | +47 | +27 | +167 |
| 02-Aug-26 | +2.6 | +51 | +38 | +158 |
| 09-Aug-26 | +0.8 | +50 | +42 | +165 |
| 16-Aug-26 | +6.9 | +53 | +47 | +143 |
| 23-Aug-26 | +0.4 | +53 | +45 | +135 |
| 30-Aug-26 | +0.7 | — | +55 | +155 |
| 06-Sep-26 | +3.8 | +49 | +39 | +147 |
| 13-Sep-26 | -4.4 | +55 | +53 | +33 |
| 20-Sep-26 | +4.8 | +13 | +31 | +43 |
| **27-Sep-26** | **−3.80** | **+24.55** | **+38.73** | **+35.24** |
