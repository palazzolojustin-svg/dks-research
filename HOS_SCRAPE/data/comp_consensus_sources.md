# DKS comp consensus sources (web scrape)

Convention: FYxxQy per CSV (FY25Q1 = qtr ended 2025-05-03). Consensus value = median of listed figures. Provider often unnamed by outlet.

- **FY18Q4** (2019-02-02): actual -2.2, consensus -3.3, beat 1.10 pp. Coresight (consensus est.) -3.3 https://coresight.com/?p=80143 | actual: shifted basis; https://coresight.com/?p=80143
- **FY19Q1** (2019-05-04): actual 0.0, consensus -1.3, beat 1.30 pp. Coresight (consensus est.) -1.3 https://coresight.com/?p=89419; Chain Store Age (analysts expected) -1.3 https://chainstoreage.com/finance-0/dicks-q1-tops-street-raises-outlook | ChainStoreAge URL: figure per search snippet, not confirmed on fetch | median of 2 | actual: flat
- **FY19Q3** (2019-11-02): actual 6.0, consensus 2.9, beat 3.10 pp. Wall Street avg (SGB, provider unnamed) 2.9 https://sgbonline.com/?p=172222 | actual: https://sgbonline.com/?p=172222
- **FY22Q3** (2022-10-29): actual 6.5, consensus -2.2, beat 8.70 pp. Schaeffers Research (analysts, provider unnamed) -2.2 https://www.schaeffersresearch.com/content/news/2022/11/22/dicks-sporting-goods-reports-q3-beat-and-raise | Bloomberg -3.1 reported in search snippet only (https://www.bloomberg.com/news/articles/2022-11-22/dick-s-boosts-forecast-after-sales-earnings-beat-estimates; not fetchable) excluded from value
- **FY22Q4** (2023-01-28): actual 5.3, consensus 2.1, beat 3.20 pp. CNBC via Retail Customer Experience 2.1 https://www.retailcustomerexperience.com/news/dicks-sporting-goods-q4-sales-are-a-hit-out-of-the-park/ | CNBC original not fetched
- **FY23Q3** (2023-10-28): actual 1.7, consensus -1.9, beat 3.60 pp. Analysts avg (SGB, provider unnamed) -1.9 https://sgbonline.com/?p=298541 | sign looks odd vs actual +1.7 but as printed by SGB
- **FY23Q4** (2024-02-03): actual 2.8, consensus 0.8, beat 2.00 pp. Wall Street (Bloomberg headline article) 0.8 https://www.bloomberg.com/news/articles/2024-03-14/dick-s-sporting-goods-dks-rises-as-sales-surpass-expectations | figure from search snippet; Bloomberg page not fetchable
- **FY24Q1** (2024-05-04): actual 5.3, consensus 2.45, beat 2.85 pp. Sportico (expected) 2.4 https://www.sportico.com/business/finance/2024/dicks-stock-surges-amid-positive-outlook-1234782191/; Bloomberg via Spokesman-Review/WaPo 2.5 https://www.spokesman.com/stories/2024/may/29/dicks-sporting-goods-defies-woes-of-athletic-wear-/ | median of 2
- **FY24Q3** (2024-11-02): actual 4.3, consensus 2.5, beat 1.80 pp. Investing.com (forecast) 2.5 https://www.tradingkey.com/news/stocks/240213650-investing | company release says 4.2% (CSV actual 4.3 left unchanged)
- **FY25Q2** (2025-08-02): actual 5.0, consensus 3.2, beat 1.8 pp. C01_SYNTHESIS_B L1217-1219/C06_R1 › JPM Consensus Metrix 3.3, Wells FactSet 3.2, Barclays BBG 3.1 (SRC 03 2025-09-05 Barclays; 09-03 JPM; 09-04 WF); mean of 3
- **FY25Q3** (2025-11-01): actual 5.7, consensus 3.5, beat 2.2 pp. C06_R1 L467/693, C01_SYNTHESIS_B L1118 › JPM Consensus Metrix 3.3, Barclays BBG 3.5, one broker 3.7 (R1 L693); mean of 3
- **FY25Q4** (2026-01-31): actual 3.1, consensus 2.13, beat 0.97 pp. C06_R2 L47,125,365; C01_SYNTHESIS_B L1465 › JPM Consensus Metrix 2.1, UBS 2.1 (pre) / 2.2 (post-print); buyside bar ~3.0; mean of 3
- **FY26Q1** (2026-05-02): actual 6.0, consensus 3.4, beat 2.6 pp. C06_R3 L223,296; C06_R4 L110 › UBS cons 3.3, JPM Consensus Metrix 3.4 (5/22) / 3.5 (5/27); buyside bar ~5.0; mean of 3
- **FY26Q2** (2026-08-01): actual 4.9, consensus 4.6, beat 0.3 pp. C01_SYNTHESIS_B L1240,1241; SRC UBS 2026-08-18/08-30 › UBS cons 4.7 (8/12 preview), 4.5 (8/30 pre-print, JPM mkt bar ~4.5); mean of 2; broker/Consensus-Metrix only, no direct Bloomberg line

## No consensus comp found
FY18Q1, FY18Q2, FY18Q3, FY19Q2, FY19Q4, FY20Q1, FY20Q2, FY20Q3, FY20Q4, FY21Q1, FY21Q2, FY21Q3, FY21Q4, FY22Q1, FY22Q2, FY23Q1, FY23Q2, FY24Q2, FY24Q4, FY25Q1

## Data flags
- Company-release comps differ from existing CSV actuals: FY21Q4 (source says 5.9 vs CSV 5.0), FY22Q2 (-5.1 vs -5.4), FY24Q3 (4.2 vs 4.3), FY24Q4 (6.4 vs 6.6). Existing rows left unchanged; beats for FY24Q3 use CSV actual.
- FY18 quarters: calendar-shift adjusted headline comps used. FY20Q1 actual not located.
- Consensus comps are rarely published; all searches of CNBC/Reuters/MarketWatch were blocked or empty (cnbc/bloomberg not fetchable).
