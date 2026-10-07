# WA7 (wave 2): RAW SOURCE re-read of DKS management and expert transcripts for thesis #2 (store labor/SG&A) and thesis #1 (HoS productivity)
Agent WA7 | 2026-10-07 | Scope: SOURCE\02_DKS_TRANSCRIPTS\: 7 earnings calls (Q3 FY24 → Q2 FY26), 7 conferences (GS Sep-24/Sep-25/Sep-26, Barclays Dec-24, MS Dec-24/Dec-25, JPM Apr-26), AGM raw transcript 2026-06-10, FL deal call 2025-05-15, 14 AlphaSense expert calls, 5 investor-deck slide-text files, plus targeted reads of the annual reports.
Method: case-insensitive Grep for labor, payroll, hours, staffing, teammate, associate, operating/store model, specialist, lead, scheduling, workforce, healthcare, wage, SG&A, leverage, running hard, productivity, efficiency, self-checkout, flexibility, retention, relocation and cannibalization. I then read every hit's surrounding passage in full.
Novelty: each item was Grep-checked against the digest, the FL_EUROPE_SCRAPE primers, KNOWN_BRIEF, wave1\* and the wave2 files present at check time (WA1, WA2, WA3, WA6, L1). 10-K items (headcount, the $191.7M wage investment, the Business Optimization analog) are left to WA1, which already has them.
Script: THESIS_SCRAPE\scripts\WA7_transcript_term_counts.py → raw\WA7_transcript_term_counts.csv, raw\WA7_analyst_questions_cost.txt
Variance constants: FY27E DSG revenue $15,203M; 10bp DSG margin = $15.2M = $0.124/sh; $1M pre-tax = $0.00814/sh.

## Top findings (ranked)

[WA7-1] **Neither the Street nor management has engaged with the store-labor redesign in two years of transcripts.**
- Corpus: 14 management transcripts from 2024-09-05 to 2026-09-14 (7 earnings calls, 7 conferences) plus the AGM.
- Management raised the store labor redesign exactly once: a GAAP-exclusion line in Gupta's Q2 FY26 prepared remarks: "approximately $15 million of costs associated with redesigning the store labor model for the DICK'S Business" (2026-08-25, l.334).
- The redesign is absent from:
  - Hobart's Q2 FY26 DICK'S-business remarks, even though the rollout ran "this summer" (l.196-264);
  - the whole Q1 FY26 call (2026-05-27), six weeks after the 2026-04-14 release;
  - GS 2026-09-14, despite a direct SG&A flow-through question;
  - the AGM (no Q&A was read out; written answers were posted to the IR site).
- Analyst questions: none, in any transcript, asked about DKS store labor, store payroll, hours or the operating model. My script found 65 analyst question segments touching cost, SG&A, margin or flow-through. The only labor-related questions were Goldman's standard, generic macro questionnaire items ("materials, labor, maybe even tariffs", 2024-09-05; "freight, wages, and materials", 2025-09-04).
- Healthcare was never mentioned in the corpus until Q2 FY26 (2 hits) and GS Sep-26 (2 hits).

| Sep-2024 to Sep-2026 | SOURCE\02_DKS_TRANSCRIPTS\earnings_calls\*.md, conferences\*.md, events\DKS_Annual-Meeting-RAW-transcript_2026-06-10.md | accessed 2026-10-07 | method: python term and analyst-question classifier (scripts\WA7_transcript_term_counts.py; regex fixed for "elaborate" false positives) + manual reads | NEW calc. It extends D07-1 ("nothing said at GS 9/14") to the full corpus. | conf H (transcripts complete for these events; the Q4 FY24 call transcript is missing from the corpus) | SUPPORTS | thesis #2 | variance: no direct number. It supports the claim that consensus's ~+22bp FY27 SG&A leverage is not built on redesign savings: nobody has asked for them and management has not offered them. Caveat: absence from transcripts does not prove absence from models. D07 found no broker sizing either.

[WA7-2] **A 13-month, dated trail of AI labor scheduling preceded the redesign. Store labor savings at big-box retailers typically follow this sequence: a demand-based scheduling tool comes first, then the role and structure change.**

| Date | Speaker / event | Quote |
|---|---|---|
| 2025-08-28 | Hobart, Q2 FY25 call | "we have AI embedded in many of these tools ... as is teammates scheduling and product and merch assortment planning ... this is a very significant part of how we're driving productivity and also empowering our teammates to spend more time with athletes in a sales and service mode rather than on tasking." |
| 2025-12-03 | Hobart, MS conference | "we have experiments going ... we've got things going on with labor management planning and sort of more machine learning." |
| 2026-03-12 | Hobart, Q4 FY25 call (l.1007-1010) | "the opportunity to make our teammates more efficient and to remove a lot of manual work ... We're using that AI right now in terms of store labor forecasting." |
| 2026-03-12 | Hobart, same call (l.263-265) | "In our stores, we're evolving our service and selling culture. We're putting a bigger emphasis on relationship building and giving teammates better training and tools ... very much an ongoing journey." This previews Built to Win's role split one month early. |
| 2026-04-14 | Press release | Store operating model (KNOWN). |
| 2026-08-25 | Q2 FY26 | $15.3M charge (KNOWN). |
| 2026-09-14 | Hobart, GS conference | "efficiencies for our teammates, so we're taking work that has been formerly full of friction away from them." |

- Correction to KNOWN_BRIEF: "AI in store labor forecasting" is from the Q4 FY25 call (2026-03-12, l.1010), not Q1.

| 2025-08-28 to 2026-09-14 | SOURCE\...\earnings_calls\DKS_Q2-FY2025_Earnings-Call_2025-08-28.md l.943-954; conferences\DKS_MorganStanley-Conference_2025-12-03.md l.899-903; earnings_calls\DKS_Q4-FY2025_Earnings-Call_2026-03-12.md l.263-265, l.1006-1012; conferences\DKS_Goldman-Conference_2026-09-14.md l.786-788 | accessed 2026-10-07 | method: read | BURIED. "teammates scheduling", "tasking" and "remove a lot of manual work" have 0 hits anywhere in CORE/WORKING/THESIS, so they are SOURCE-only. "relationship building" is only in C02B. The Mar-26 forecasting quote is DUP. | conf H on the quotes; M on the read-across | SUPPORTS | thesis #2 | variance: none stand-alone. Combined with WA1-1 (the FY25 non-format headcount build), it makes savings more credible: the tool to cut hours to demand was live before the roles were redesigned. The sequencing argument draws on general retail knowledge, so treat it as INFERENCE.

[WA7-3] **The CFO is signalling an SG&A pivot from "invest" to "flex and productivity".**

| Date | Event | Quote / content |
|---|---|---|
| 2025-12-03 | Gupta, MS conference (asked about HoS pressure on SG&A) | "2026, we'll opening a new distribution center, so there may be an investment ... But then ... we have plenty of flexibility in our cost structure from an SG&A to be able to deliver a bottom line improvement, even with those investments." |
| 2026-09-14 | Gupta, GS conference (to McShane's "running hard" / weak flow-through) | "it's not lost on us and we are consciously focused on that ... the SG&A intensity will also get benefited from the negotiations that we are having from a synergy perspective." |
| 2025-05-15 | FL deal call | Gupta had said the synergies include "opportunities on the SG&A line when you think about the procurement opportunities that we see across the company". |

- Together these imply that part of the $100-125M synergy (non-merchandise procurement) lands in DICK'S segment SG&A, not only in FL.

| 2025-05-15 to 2026-09-14 | SOURCE\...\conferences\DKS_MorganStanley-Conference_2025-12-03.md l.1003-1012; DKS_Goldman-Conference_2026-09-14.md l.535-561; events\DKS_Foot-Locker-Acquisition-Call_2025-05-15.md l.366-370 | accessed 2026-10-07 | method: read | BURIED ("plenty of flexibility" is only in C02B/C03B/C01A; "not lost on us" and "SG&A intensity" are SOURCE-only). The GS "collective work … on productivity" quote is DUP (F3-9); "collective company synergy" is DUP (digest). | conf M (management claims) | SUPPORTS | thesis #2 | variance (INFERENCE): if 10% of the synergy midpoint ($11M) is non-merch procurement booked in DICK'S SG&A, that is ~7bp ≈ +$0.09/sh. It is unclear whether consensus credits synergy to the DICK'S segment; low weight.

[WA7-4] **The last time DKS lapped a discrete SG&A investment wave, deleverage moderated by about 68bp, to roughly flat, not to leverage. That sets the bar for Built to Win.**
- Q1 FY25 call (2025-05-28), Gupta: "greater SG&A expense deleverage in the first half, with moderation in the second half as we lap the higher investment levels from the second half of the last year".
- Delivered DICK'S SG&A y/y, sales-weighted (quarterly bp DUP from digest; weighting is mine):
  - 1H FY25: Q1 −42bp on $3,174.7M, Q2 −105bp on $3,646.6M → **−75.7bp**.
  - 2H FY25: Q3 −45bp on $3,236.9M, Q4 +22bp on $4,050.8M → **−7.8bp**.
  - Moderation: about +68bp.
- The same weighting for 1H FY26 (Q1 −31bp on $3,377.4M, Q2 −96bp on $3,849.9M) gives **−65.6bp**.
- INFERENCE: if FY27 simply laps the FY26 wave (World Cup marketing, HoS pre-open timing) with the same ~68bp moderation, 1H FY27 SG&A ends about flat (+2bp).
  - Consensus needs ~+22bp of FY27 SG&A leverage, so the pure "lap" effect only gets DKS to roughly consensus-minus.
  - Beating consensus requires structural labor savings (Built to Win, AI scheduling) on top.
  - This sharpens the thesis: the redesign is what separates consensus from upside. It also warns that without it there is no beat.
- Credibility check: the other leverage promises failed.
  - Q2 FY25: SG&A leverage "at a low single digits comp" (DUP F3) did not happen at a 4.5% comp.
  - Q1 FY26 Hobart: "We're absolutely expecting leverage for the full year ... in the second half" (2026-05-27 l.501-502). It was withdrawn 90 days later (DUP digest).

| FY25-FY26 | SOURCE\...\DKS_Q1-FY2025_Earnings-Call_2025-05-28.md l.283-286; DKS_Q1-FY2026_Earnings-Call_2026-05-27.md l.493-505; digest §2b/§2c/l.67 (quarterly bp, sales) | accessed 2026-10-07 | method: read + sales-weighted arithmetic | NEW calc (quote BURIED in C01A; bp DUP) | conf M (the DICK'S SG&A bp mix consolidated pre-FL quarters with DICK'S-only post-FL quarters) | NEUTRAL (bar-setting) | thesis #2 | variance: frames the base case at ≈ consensus. The upside rests on WA1-1 and D07-2 (personnel), not on lapping.

[WA7-5] **Company-stated headcount: "~60,000" DICK'S Business teammates. This independently confirms WA1's derived FY25 build, and the post-rollout deck still shows no cut.**

| Investor deck | Teammates (DICK'S Business) | Engagement |
|---|---|---|
| Dec-2025 | "50,000+" | ~84% recommend, Medallia 2025 |
| Mar-2026 | "50,000+" | ~86%, Medallia 2026 |
| May-2026 | **"~60,000"** | ~86% |
| Aug-2026 | **"~60,000"** | ~86% |

- The Q4 FY23 letter said 55,000. WA1 derived FYE25 ≈ 59,800 by subtracting FL's 45,400 from the 10-K total.
- The Aug-2026 deck, published after the summer rollout, did not lower the figure. So there is no disclosed net headcount reduction yet. The labor $ test remains the Q3 FY26 10-Q.

| Dec-2025 to Aug-2026 | SOURCE\02_DKS_TRANSCRIPTS\slides_text\DKS_Q3-FY2025_Investor-Presentation-Dec-2025_slide-text.md l.583-595; DKS_Investor-Presentation_2026-03 l.521-535; DKS_Q1-FY2026_Investor-Presentation-May-2026 l.521-535; DKS_Q2-FY2026_Investor-Presentation-Aug-2026 l.527-541 | accessed 2026-10-07 | method: read across decks | BURIED (the "~60,000" step-up is only in C05 l.1275; Medallia % is DUP F4) | conf M (rounded marketing figure) | NEUTRAL (corroborates WA1-1's size of the prize; no evidence of cuts yet) | thesis #2 | variance: none direct.

[WA7-6] **AGAINST: service intensity is part of the moat, and management frames the stores as a service investment. Savings are likely to be partly recycled.**
- Hobart, Barclays 2024-12-03: "the service model, the team, the investment in people and training ... the secret sauce behind our success".
- Supplier expert, 2026-07-08 (Director of Sales, premium apparel brand): "They have great staffing, customer service" and "They have a lot of store associates throughout the store. They approach you."
- Supplier expert, 2026-07-14 (Planning Manager, global athletic brand): to beat run-specialty doors DKS "has to retrain their support staff ... which is very, very difficult to do". That is the gap the new footwear "Specialists" target, a cost-adding role.
- Healthcare: Hobart GS 2026-09-14: "conservatism toward fuel costs and health care costs, which we have been experiencing all year" and "exogenous impacts from fuel and health care". So healthcare sat inside the 1H FY26 personnel deleverage (+44bp, KNOWN) from Q1 but was first disclosed in August. It does not lap in FY27 (Mercer +8.2%, D02-6).
- Gupta GS 2024-09-05 predicted 2025 cost pressure "especially on the labor side", which then showed up as FY25 personnel deleverage in Q2-Q4.
- Gupta GS 2025-09-04: "Our retention rates are at a phenomenal right now". Low attrition means a redesign can't shrink by natural turnover alone. That fits the "demoted" (not exited) employee evidence in D07-3 and suggests savings ramp more slowly (INFERENCE).

| 2024-09-05 to 2026-09-14 | SOURCE\...\conferences\DKS_Barclays-Conference_2024-12-03.md l.371-377; expert_calls_alphasense\DKS_Expert-Call_2026-07-08_Director-of-Sales_Premium-Apparel-Accessories-Brand_DKS-account.md l.243, l.344; DKS_Expert-Call_2026-07-14_Planning-Manager_Global-Athletic-Brand_forecasting-inventory.md l.220; conferences\DKS_Goldman-Conference_2026-09-14.md l.209-217; DKS_Goldman-Conference_2024-09-05.md l.971-975; DKS_Goldman-Conference_2025-09-04.md l.807-814 | accessed 2026-10-07 | method: read | BURIED (in C03A/C03B/C04 only; 0 hits in digest/primers/KNOWN/wave files) | conf M | AGAINST | thesis #2 | variance: supports a 30-50% haircut to gross savings (consistent with WA1-3). Healthcare at +8.2% on ~$200M ≈ −11bp (D02-6) partly offsets.

[WA7-7] **Thesis #1: the raw transcripts hold no per-store HoS/FH number beyond what is already known.** Every HoS sales, productivity, cannibalization and relocation passage was re-read: the GS Sep-24 / Barclays Dec-24 / MS Dec-24 / Q3 FY24 "stay in comp" remarks, Ross Park, Katy/Baybrook, the FH footwear deck "50% bigger", A-mall volumes "meaningfully higher", "out of this world", "comping the comp" in years 2-4, the "gross before cannibalization" slide footnote and supplier UGG +238%. All are already surfaced by F1, F3 and F4.
- The only residual items are minor:
  - GS 2024-09-05 (Gupta): HoS needs "100,000 to 120,000 square foot" sites "in the right node". FY24 plan was 8 HoS (actual 7) and ~15 for 2025 (actual 16), so delivery against plan was ~±1 per year.
  - Q2 FY25 Gupta (2025-08-28): "even some of the smaller markets are able to support the House of Sport locations very, very productively" (F3-5c, DUP).

| method: Grep "(House of Sport|Field House).{0,200}(\$|%|per square|volume|productiv|cannibal|halo)" + reads | DUP/minor | NEUTRAL | thesis #1 | variance: none.

## Smoking-gun candidates
1. **WA7-1 (Street blind spot).** "In two years and 14 transcripts, not one analyst has asked DICK'S about store labor, and management mentioned the redesign once, as a GAAP add-back." A PM will remember it, and it is checkable. It is the cleanest evidence that the labor reset is outside the consensus debate. Pair it with WA1-1 (the size of the prize) and the Q3 FY26 10-Q personnel line (the proof point).
2. **WA7-2 (AI scheduling → role redesign sequence).** It shows that Built to Win is the second step of a 13-month program that began with AI demand-based scheduling, not a reactive cut. It strengthens the credibility of savings, though it does not size them.
3. **WA7-4 (the lap analog sets the bar).** This is the honest framing: lapping alone gets FY27 SG&A to about flat, and the redesign is what beats consensus's ~+22bp.

## Evidence against / caveats
- WA7-6: service-moat language and supplier praise for "great staffing" both point to recycled savings. The footwear Specialists add cost. Healthcare is persistent, not one-off, and was "experienced all year". Low attrition slows a headcount-led reset.
- WA7-4: the 2H FY25 lap only got SG&A to −8bp, not to leverage. Management's SG&A leverage promises failed in 2 of 3 cases (Q2 FY25 "low single digits comp", Q1 FY26 "absolutely expecting leverage").
- WA7-5: the post-rollout Aug-2026 deck still states ~60,000 teammates, so there is no disclosed headcount cut yet.
- Management never mentioned savings and chose not to promote the redesign on calls. It may be designed as reinvestment (service roles), not cost-out.
- The Q4 FY24 call transcript (2025-03-11) is missing from the corpus, so the corpus misses one quarter of SG&A guidance language.

## Avenue assessment
| Avenue | Access | Signal 1-5 | Script / path |
|---|---|---|---|
| Raw earnings-call transcripts (7) | open | 3 (labor redesign absent; AI scheduling trail; lap-guidance language) | scripts\WA7_transcript_term_counts.py |
| Raw conference transcripts (7) | open | 3 (CFO flex/productivity/"running hard" responses; retention; labor-pressure history) | same |
| AGM raw transcript 2026-06-10 | open | 1 (no Q&A read out; answers posted to the IR site) | — |
| FL deal call 2025-05-15 | open | 2 (SG&A procurement synergies) | — |
| Expert calls (14) | open | 1-2 (no DKS labor data; staffing/service anecdotes only) | — |
| Investor-deck slide text (5) | open | 2 (teammate count step-up 50,000+ → ~60,000) | — |
| Annual reports (10-K MD&A, human capital) | open | (WA1's territory, already covered: $191.7M/$127.1M wage investments, BO analog, headcount) | — |
| Analyst-question classifier | open | 4 (quantifies the blind spot) | raw\WA7_analyst_questions_cost.txt |

## Leads for next wave
- **AGM written Q&A (posted after 2026-06-10):** investors.dicks.com, under annual-meeting materials or "stockholder questions". It may hold a shareholder question on the store model or headcount. Try the IR Q4 JSON feed (scripts\D07_q4feed.py) for a 2026 AGM Q&A PDF, and Wayback CDX for investors.dicks.com/*annual-meeting*.
- **Q3 FY26 call (2026-11-24/25):** this is the first time an analyst could ask. Suggested question for the pitch: "What hours or payroll savings does the summer store operating model deliver in FY27, net of Specialist roles?" Watch whether "store labor model" appears in Hobart's remarks.
- **Q4 FY24 call transcript (2025-03-11), missing from the corpus:** FactSet/CallStreet or the IR webcast replay. It holds the FY25 SG&A investment framing that the 2H FY25 "lap" refers to.
- **Medallia/engagement and the teammate count in the next deck (Q3 FY26, ~Dec 2026):** if "~60,000" changes or the engagement score drops, that is a read on the redesign's scale and on its service risk.
- **AI scheduling vendor:** the Aug-2025 and Mar-2026 quotes say the tool is "in our app" and does "store labor forecasting". Search the careers site, LinkedIn and vendor case studies for the vendor (e.g. UKG, Legion, Zebra/Reflexis, Workforce.com; DKS has not named one) and any stated hours savings.
- **Synergy allocation:** ask brokers (or check JPM's "$12M GP + $50M SG&A" 2026 synergy model, digest §4c) whether any synergy SG&A sits in the DICK'S segment (WA7-3).

## Dead ends / blocked
- No transcript contains any number on store hours, payroll per store, headcount change, Specialist or lead counts, or redesign savings.
- The expert calls are all supplier-side, with no DKS store-operations interviewee. Every "labor" hit is supplier manufacturing cost.
- AGM: procedural only.
- No HoS per-store sales/traffic number exists in the raw transcripts beyond the known slide economics.

## Duplicates skipped
- $15.3M/$21M redesign charge; ~$5.7M left in 2H (L1/WA2).
- "AI in store labor forecasting" (KNOWN; corrected to Q4 FY25).
- GS 9/14 "collective work … on productivity" and capex productivity (F3-9).
- Q2 FY26 Q3 ~50bp SG&A deleverage and Q4 leverage (digest l.146).
- SG&A leverage "at a low single digits comp" (F3).
- Medallia 84%/86% and +1,585/+2,070bp (F4).
- RFID "labor productivity" (F3 T2-a).
- Ross Park, Katy/Baybrook, Prudential, "comping the comp", A-mall "meaningfully higher", "out of this world", FH footwear 50% bigger, mall traffic / sales psf (F1/F3).
- Slide "gross before cannibalization" (F1/F2/F4).
- Stripers payroll (digest).
- 10-K headcount series, $191.7M/$127.1M hourly wage investments, Business Optimization $26.7M severance and 78bp moderation, incentive comp (WA1).
- Healthcare +8.2% (D02-6).
- Ship-from-store ~90% (digest).
- Expert UGG +238% and "traffic up" (digest E-table).

STATUS: COMPLETE

