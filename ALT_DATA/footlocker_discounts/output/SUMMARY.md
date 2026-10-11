# Foot Locker discount scrape (NA + EMEA), Sep 2024 – Oct 2026

Built 2026-10-11 from Common Crawl archives. Chart: `fl_discount_chart.png`. Data: `monthly_metrics.csv`, `pages_per_month.csv`.

## Headline

- **Foot Locker NA put fewer products on sale in 2026 than in 2025.** Mar–Sep average: **41% of products on sale (2025) → 30% (2026)**. Average discount across all products: **13.3% → 9.5%**.
- **How deep each discount goes didn't change** (about 31–33% off for items on sale, both years). The drop is in *how many* items are discounted, not *how much*.
- **The drop shows up everywhere we sliced it:** US only (38% → 28%), Nike/Jordan (40% → 29%), other brands (42% → 32%), category pages (42% → 31%) and `/buy/` pages (41% → 30%). So it isn't caused by Canada, brand mix or page-type mix.
- **EMEA:** 42% of products on sale in Sep–Nov 2025, then **about 23% from Jan–Sep 2026**. The average discount fell from 14.9% to 6.6%. The step down came in Dec 2025, and it shows in the UK, Germany and France individually.
- **The Dick's deal (closed 2025-09-08)** comes right before the decline in both regions. My interpretation: this fits less discounting under new ownership, but the data can't prove the cause.

## Conflicts with the research notes (flagged, not resolved)

- Dick's said Q2 FY26 (May–Jul 2026) was an "increasingly aggressive promotional environment" that hit Foot Locker hardest. Foot Locker's gross margin was 25.7%, with "promo on legacy silhouettes" (`CORE_NOTES/00_CORE_DIGEST.md` › Q2 FY26 print, 2026-08-25).
- The scrape shows **no rise in the share of website products on sale** in May–Aug 2026 compared with 2025. There's a small bump in Jun 2026 (34%), but it's still below Jun 2025 (43%).
- **Possible reasons (my inference):** discounts given at checkout (promo codes, loyalty offers, bundles) or in stores never show up as list price vs. sale price on category pages. Price-matching on specific products would also barely move a share-of-products measure. The margin hit could also be clearance sold through other channels.

## Monthly results

The capture window is the dates within each month when Common Crawl's crawler visited.

| Month | NA pages | NA % on sale | NA avg disc | US % on sale | EMEA pages | EMEA % on sale | EMEA avg disc | Capture window |
|---|---|---|---|---|---|---|---|---|
| 2024-09 to 11 | 0 | – | – | – | 0 | – | – | Common Crawl blocked by Foot Locker |
| 2024-12 | 46 | – | – | – | 1 | – | – | too few pages |
| 2025-01 | 2,741 | 47.7% | 15.5% | 46.1% | 0 | – | – | Jan 12–25 |
| 2025-02 | 0 | – | – | – | 0 | – | – | blocked |
| 2025-03 | 5,553 | 39.5% | 13.4% | 38.2% | 0 | – | – | Mar 15–28 |
| 2025-04 | 5,537 | 41.1% | 13.1% | 36.3% | 16 | – | – | Apr 17–30 |
| 2025-05 | 2,423 | 42.7% | 13.7% | 39.3% | 10 | – | – | May 12–25 |
| 2025-06 | 4,016 | 43.0% | 13.8% | 39.1% | 23 | – | – | Jun 12–25 |
| 2025-07 | 3,775 | 41.8% | 13.3% | 36.1% | 17 | – | – | Jul 8–20 |
| 2025-08 | 6,318 | 41.7% | 13.5% | 37.5% | 12 | – | – | Aug 2–15 |
| 2025-09 | 5,587 | 38.6% | 12.2% | 36.6% | 8,169 | 43.2% | 12.1% | Sep 5–18 |
| 2025-10 | 6,119 | 37.4% | 12.0% | 34.2% | 1,085 | 40.1% | 16.2% | Oct 5–18 |
| 2025-11 | 6,286 | 25.8% | 9.5% | 23.9% | 2,862 | 43.8% | 16.5% | Nov 6–19 (before Black Friday) |
| 2025-12 | 5,891 | 36.1% | 13.1% | 34.9% | 3,905 | 18.9% | 7.5% | Dec 4–17 |
| 2026-01 | 5,930 | 34.8% | 13.4% | 34.2% | 2,165 | 20.5% | 7.3% | Jan 12–25 |
| 2026-02 | 4,223 | 22.2% | 6.8% | 17.4% | 2,741 | 17.9% | 4.9% | Feb 6–19 |
| 2026-03 | 2,464 | 31.1% | 9.1% | 27.1% | 2,868 | 23.3% | 8.3% | Mar 5–17 |
| 2026-04 | 2,451 | 32.0% | 9.8% | 30.5% | 2,820 | 25.4% | 7.1% | Apr 10–23 |
| 2026-05 | 2,473 | 25.8% | 8.3% | 25.6% | 2,134 | 11.9% | 2.8% | May 8–21 |
| 2026-06 | 2,470 | 34.1% | 10.7% | 31.6% | 2,712 | 26.2% | 5.2% | Jun 5–18 |
| 2026-07 | 2,429 | 29.0% | 9.2% | 26.1% | 5,020 | 28.7% | 8.5% | Jul 10–23 |
| 2026-08 | 2,306 | 30.8% | 9.9% | 28.3% | 2,801 | 24.2% | 7.1% | Aug 7–19 |
| 2026-09 | 2,453 | 29.1% | 9.7% | 25.9% | 2,038 | 27.5% | 8.3% | Sep 4–17 |
| 2026-10 | 0 | – | – | – | 0 | – | – | no crawl yet |

**Totals:** 122,890 pages with prices and 2.65M product price readings. NA averages **3,134 pages a month** (20 of 26 months have 2,000+). EMEA has 12 months with 2,000+ (Sep 2025 – Sep 2026, except Oct 2025 at 1,085).

## Method

1. **Source:** Common Crawl's index for all 25 crawls from Sep 2024 to Sep 2026, filtered to Foot Locker storefronts. NA = footlocker.com and footlocker.ca. EMEA = every Foot Locker Europe country site found; UK, Germany, France and the Netherlands make up most of it.
2. **Pages:** archived category, `/buy/` and search listing pages (status 200), downloaded straight from the crawl archive files. NA was capped at 2,500 randomly chosen pages per month in each crawl. EMEA took every page.
3. **Prices:** read from the page's embedded product data. Category grids give `originalPrice` vs `price`. `/buy/` grids give `price_range` list price vs purchase price.
4. **Unit:** each unique product per region per month. A product seen several times in a month is averaged.
   - % on sale = share of products priced more than 0.5% below list.
   - Avg discount = average of (1 − price / list) across *all* products, counting full-price items as 0 (the same as the second line on your Dick's chart).
   - Depth = the average discount among on-sale products only.
5. **Changes from your Dick's method:**
   - Added `/buy/` pages. They're Foot Locker's search landing pages, with the same price fields.
   - Swapped the "national brand" split for Nike/Jordan vs. other brands, since nearly everything Foot Locker sells is a national brand.

## Caveats

- **Gaps:** Foot Locker blocked Common Crawl's crawler in Sep–Nov 2024 and Feb 2025, so those months have no data. The Wayback Machine (the planned backup) is blocked from this cloud environment, and other web archives were too.
- **EMEA before Sep 2025** has fewer than 25 pages a month, too few to use, so it's left blank.
- **Timing:** each month is a roughly 2-week snapshot (see the capture windows). The Nov 2025 dip (captured Nov 6–19) probably reflects the weeks just before Black Friday, not the whole month.
- **Canada** runs a much higher on-sale share than the US (44–62% vs 24–38% in Aug–Dec 2025), so the NA total moves a little with Canada's share of the pages. The US-only column removes that effect.
- **What the method misses:** only prices visible on the page count. Checkout codes, loyalty offers and in-store markdowns don't show up.
- **Size of the 2025 sample:** some 2025 NA months have more than 2,500 pages, because restarts sampled extra pages. That adds sample size but doesn't bias the results; the page-type split above confirms this.

## Files

- `scripts/`:
  - `cc_scrape.py`: index and download
  - `flparse.py`: price parser
  - `aggregate.py`: monthly metrics
  - `chart.py`: the chart
  - `wb_scrape.py`: Wayback scraper, unused because Wayback is blocked
  - `run_cc_fetch.sh`, `sync.sh`: run and snapshot helpers
- `data/cdx/`: Foot Locker capture index for each crawl
- `data/pages/`: every parsed page with its products, list price and price
- `output/monthly_metrics.csv`: region × month × segment. Segments: all, fmt_cat, fmt_seo, nike_jordan, non_nike, country_XX.
- `output/pages_per_month.csv`: pages, sources, page types, product readings and capture dates for each month
