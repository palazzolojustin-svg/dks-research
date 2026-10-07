# APIFY LEDGER: THESIS_SCRAPE (hard cap $25.00 total)
Budgets wave 1: H05 $8, H06 $3, H01 $3, D06 $4, reserve $7 (orchestrator).
date | agent | actor | run id | est cost $
RUNNING TOTAL: $0.00
2026-10-07 | H05 | compass/crawler-google-places (HoS US search, cap 70, no details) | jbxYps1Xc0Jhrgw4w | est 0.30 (cap 0.50)
2026-10-07 | H05 | compass/crawler-google-places (pilot 3 HoS, reviews since 2025-01-01, details) | rgpSTmy3VMxy7LXJO | est 0.40 (cap 0.60)
2026-10-07 | H05 | compass/crawler-google-places (41 HoS, reviews since 2025-01-01, details) | FhHNx8tzSHLt2GCjg | est 2.80 (cap 3.50)
2026-10-07 | D06 | apify/google-trends-scraper | Y0HS44G8lpX6m1d0H | 0.05 (cap 0.30)
2026-10-07 | H05 | compass/crawler-google-places (44 metro searches x6 DSG, no reviews) | 7eIIxp9gBgim1Beei | est 0.80 (cap 1.00)
2026-10-07 | H05 | compass/crawler-google-places (43 'DSG near <city>' searches x5, no reviews) | SlyHbkDminkjTBlkB | est 0.65 (cap 0.90). NB run 7eIIxp9gBgim1Beei actually only scraped 6 places (~0.02)
2026-10-07 | H05 | compass/crawler-google-places (search run SlyHbkDminkjTBlkB aborted at ~94 places, actual ~0.29) | - | -
2026-10-07 | H05 | compass/crawler-google-places (38 legacy/dup DSG controls, reviews since 2025-01-01, details) | 8FpKG2ugSHlSkBowF | est 2.10 (cap 2.60)
2026-10-07 | H05 | compass/crawler-google-places (US search 'DICK'S Field House', only_includes, cap 60) | vMgRQIJ6GExzgma5A | est 0.15 (cap 0.50)
2026-10-07 | H01 | apify/google-search-scraper (24 queries x1 page; WebSearch budget exhausted) | xdV2e6YxdcgzeBlE8 | est 0.11 (cap 0.50)
2026-10-07 | H05 | compass/crawler-google-places (FH search vMgRQIJ6GExzgma5A aborted: 0 places found, ~0.00) | - | -
2026-10-07 | H05 | compass/crawler-google-places (9 non-DKS retail + 6 Academy controls, reviews since 2025-04-01) | C5az5B9LrSZTpcg33 | est 1.00 (cap 1.30)
2026-10-07 | H04 | apify/google-search-scraper (20 landlord/REIT HoS queries; ABORTED after 12 by Apify account billing-cycle limit) | Wp7YdeqmPqdFEvtHy | est 0.05 (cap 0.50). NOTE: Apify account reports 'maximum usage for current billing cycle' reached
2026-10-07 | D06 | apify/google-trends-scraper | Y0HS44G8lpX6m1d0H | correction: ABORTED, 0 results, ~0.00
2026-10-07 | D06 | data_xplorer/google-trends-fast-scraper | C7WROOy8MXttvjhF5 | 0.02
2026-10-07 | D06 | apify/rag-web-browser | koGAEFuSr3kwqKAm2 | 0.02
2026-10-07 | D06 | thewolves/appstore-reviews-scraper | (rejected: Apify 'Monthly usage hard limit exceeded') | 0.00
2026-10-07 | H05 | compass/crawler-google-places (12-listing 2023+ ramp history) | REFUSED by Apify: 'Monthly usage hard limit exceeded' (account-level cap, not THESIS ledger) | 0.00
2026-10-07 | H05 | ACTUALS RECONCILED (PPE: place 0.003 + detail 0.002 + review 0.0005 + filter 0.001): jbxYps 46 pl ~0.19; rgpSTm 3 pl+458 rev ~0.25; FhHNx8 41 pl+4268 rev ~2.34; 7eIIxp 6 pl ~0.02; SlyHbk ~94 pl ~0.29; 8FpKG2 36 pl+2404 rev ~1.38; vMgRQI 0 pl ~0.00; C5az5B 9 pl+1106 rev ~0.60 | H05 TOTAL ~5.07
NOTE ~05:00: H05 spent ~$5.07 (see its lines above if logged). Apify account then returned 'Monthly usage hard limit exceeded' - Apify unusable for the rest of the run.
2026-10-07 | H01 | NOTE: next apify/google-search-scraper call refused 'Monthly usage hard limit exceeded' (account-level cap; no run created, ) | - | 0.00
