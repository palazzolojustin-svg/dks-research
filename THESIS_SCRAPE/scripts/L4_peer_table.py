"""L4: peer store-labor-model programs (hand-entered from EDGAR text pulled by L4_peer_sentences.py / L4_cik_grep.py and
news articles in raw/L4_gnews_articles.txt) -> raw/L4_peer_table.csv, plus DKS translation (INFERENCE) -> raw/L4_dks_sizing.csv
Rerun: python L4_peer_table.py
"""
import csv
RAW = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw'
rows = [
 # retailer, program, start, type, charge_$M, stated_savings_$M, realized_bps_of_sales_yr1, comp_context, time_to_show, later_reversal, source
 ('Lowe\'s', 'New store staffing / store leadership model', 'Q1 FY17 (Feb-2017)', 'cost-out (de-layer)', None, None,
  '-40 / -20 / -27 (Q1/Q2/Q3 FY17 operating salaries); FY17 -27', 'comp +1.9% / +4.5% / +4.0% FY', '1st quarter',
  'Q1 FY18 +32bp deleverage (customer-facing hours reinvested, comp +0.6%); Q2 FY18 -21bp', '10-Q 2017-06-06, 2017-09-05, 2017-12-05; 10-K 2018-04-02 (CIK 60667)'),
 ('Lowe\'s', 'Wave 2: retail fundamentals, hours from 60% tasking/40% selling (2018) to >50% selling; role eliminations', 'Q4 FY18-FY19', 'cost-out + reallocation', None, None,
  'FY18 -15 (Q4 FY18 -52) operating salaries; Q1 FY19 -80, Q2 FY19 -50 retail operating salaries; FY19 -45 salaries', 'FY18 comp +2.4%, FY19 +2.6%', '1st quarter',
  'Oct-2019 press: morale complaints (Business Insider)', '10-K 2019-04-02, 10-Q 2019-06-03, 2019-09-03, 10-K 2020-03-23, 8-K 2020-02-26 EX-99.2'),
 ('Barnes & Noble', 'New store labor model, ~1,800 store roles eliminated', 'Feb-2018', 'cost-out', 10.7, 40.0,
  'store payroll -150 (Q2 FY19), -135 (26wk), -100 (39wk), -80 FY19 (% of store sales) + benefits -40', 'comps negative (~-5%)', '1-2 quarters',
  'none disclosed; sold to Elliott 2019', '8-K 2018-02-13; 10-Q 2018-03-01; 10-Qs FY19; 10-K 2019 (CIK 890491); CNBC 2018-02-13; Business Insider 2023-02-19 (1,800)'),
 ('Big Lots', 'Operation North Star: simpler store management structure (one Assistant Leader removed in certain volume stores)', 'Q2 2019', 'cost-out', 38.3, 100.0,
  'Q4 2019 SG&A -30bp, "primarily from lower store payroll and corporate headquarters expense"', 'Q4 comp -0.9%', '2 quarters',
  'shrink +~30bp GM in Q4 2019 attributed to the labor-model transition ("slightly backfired")', '10-Q 2019 Note 9; 8-K transcripts 2019-08, 2019-12, 2020-03 (CIK 768835)'),
 ('Bed Bath & Beyond', 'Realignment of store management structure', 'Q2 FY17 (Aug-2017)', 'cost-out', 16.9, None,
  'none visible: payroll was the #1 SG&A deleverage driver in FY17', 'comps negative', 'n/a', 'further $3.9M charge Q1 FY19', '10-Q 2017-10-02; 10-K 2018-05-02 (CIK 886158)'),
 ('Designer Brands (DSW)', 'Store staffing / labor model change', 'FY2018', 'cost-out', 5.6, None, 'n/d', 'n/d', 'n/d', 'n/d', '10-Q 2018-09; 10-K 2019-2021 (CIK 1319947)'),
 ('L Brands / Victoria\'s Secret', 'VS store management structure + labor model (part of $400M profit plan incl. HQ)', '2020', 'cost-out', 81.0, 400.0,
  '2022 GA&SO -$110M "lower store selling expenses driven by improvement in our labor model"', 'sales falling', '~1 year', 'n/d', '10-Q 2020 (CIK 701985); VSCO 10-K 2022-23'),
 ('Petco', 'Optimize store labor model + cost-out (late FY24)', 'Q4 FY24', 'cost-out', None, None,
  'SG&A 37.9% -> 36.6% (-130bp) FY25, "primarily due to lower payroll and other compensation costs"', 'comps ~flat/negative', '~1 year', 'n/d', '10-K 2025-03-31, 2026-03-13 (CIK 1826470)'),
 ('Hibbett', 'Store labor efficiency + discretionary cuts', 'Q3 FY24 (Aug-Oct 2023)', 'cost-out', None, None,
  'SG&A -~90bp "including improved efficiency of store labor"', 'n/d', 'n/d', 'acquired by JD 2024', '8-K 2023-11-21; 10-Q 2023-12-05 (CIK 1017480)'),
 ('Gap Inc.', '1,800 roles: HQ + "upper field" (regional store leaders); fewer layers', 'Apr-2023', 'cost-out (mostly HQ)', 110.0, 300.0,
  'n/d (half of $300M in 2023)', 'sales falling', '<1 year', 'n/d', 'CNBC 2023-04-27 (8-K): $100-120M cost, $300M annualized'),
 ('American Eagle', '"Efficiencies in our store labor model"', 'FY23-FY24', 'offset only', None, None,
  'store comp still +$24M FY23 / +$16M 39wk FY24 "due to increased wage rates ... partially offset by efficiencies in our store labor model"', 'positive', 'n/a', 'n/a', '10-K 2024-03-15; 10-Qs 2024 (CIK 919012)'),
 ('Target', 'Store labor productivity', 'FY2019', 'offset only', None, None, '"Store labor productivity and lower incentive compensation in 2019 offset pressure from wage growth"', 'comp +3.4%', 'n/a', 'Feb-2026: reinvesting in store payroll', '8-K 2020-03-03 EX-99'),
 ('Home Depot', 'New store leadership structure ADDING floor managers', 'FY2022', 'service reinvestment', None, None,
  'SG&A 17.4% -> 18.0% (FY24) "higher payroll costs"; 18.0% -> 18.6% (FY25) "higher payroll and related costs"', 'comps negative/flat', 'n/a', 'n/a', '10-K 2023-03-15, 2024, 2025-03-21, 2026-03-18 (CIK 354950)'),
 ('Dollar General', 'Reversal after Fast Track labor productivity era: +$150M retail labor hours', 'FY2023', 'reinvestment / reversal', None, -150.0,
  '+~40bp of sales (INFERENCE: $150M / ~$38.7B FY23 sales)', 'FY23 comp +0.5%', 'n/a', 'is itself the reversal (store manager turnover, standards)', '8-K/10-Q/10-K 2023-2024 (CIK 29534)'),
 ('Walmart', 'Store lead role eliminated -> emerging store manager / coach, no layoffs, higher base pay', 'Apr-2026', 'service reinvestment', None, None,
  'n/d; emerging SM base $85-120K ($119-276K w/ bonus); coach base $65-100K', 'positive', 'n/a', 'n/a', 'Yahoo Finance 2026-04-28 (memo); HR Grapevine 2026-04-30'),
 ('Target', 'Fewer store districts (~100 roles) + ~400 supply chain roles cut; "significantly more payroll in our stores"', 'Feb-2026', 'service reinvestment', None, None,
  'n/d', 'flat sales 4 yrs', 'n/a', 'n/a', 'CNBC 2026-02-09 (internal memo)'),
 ('Sportsman\'s Warehouse', 'Reinvestment in store payroll', '1H FY25', 'service reinvestment', None, None,
  'SG&A 35.4% flat; "reinvestment into customer facing ... including store payroll"', 'positive', 'n/a', 'n/a', '8-K 2025-09-04 EX-99 (CIK 1132105)'),
]
hdr = ['retailer', 'program', 'start', 'type', 'charge_$M', 'stated_annual_savings_$M', 'realized_yr1_effect', 'comp_context',
       'time_to_show', 'later_reversal_or_cost', 'source']
with open(RAW + r'\L4_peer_table.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(hdr); w.writerows(rows)

# Savings / charge multiples where both are disclosed
mult = {r[0] + ' ' + r[2]: r[5] / r[4] for r in rows if r[4] and r[5] and r[5] > 0}
mult['DKS 2023 Business Optimization (WA1/WA2)'] = (23 + 34) / 2 / 26.7
print('savings/charge multiples:', {k: round(v, 2) for k, v in mult.items()})

# DKS translation (INFERENCE)
REV = 15203.0; BP = REV / 1e4          # $1.52M per bp
EPS_PER_M = (1 - 0.2746) / 89.09        # $/sh per $1M pre-tax
CHARGE = 21.0                           # FY26 store operating model redesign charge, $M (KNOWN)
PERS = 0.143 * REV                       # DSG personnel ~14.3% of FY27E DSG revenue
cases = [
 ('charge x DKS-2023 (0.9x)', CHARGE * 0.9),
 ('charge x Big Lots (2.6x)', CHARGE * 100 / 38.3),
 ('charge x Gap (2.7x mid)', CHARGE * 300 / 110),
 ('charge x B&N (3.7x)', CHARGE * 40 / 10.7),
 ('Lowe\'s 2017 FY 27bp x 0.85 (HoS/GG excluded)', 27 * BP * 0.85),
 ('Lowe\'s 2019 FY 45bp x 0.85', 45 * BP * 0.85),
 ('B&N FY19 store payroll -80bp x 0.85', 80 * BP * 0.85),
 ('WA3: consensus-implied -2.5% hours/sq ft on personnel', 0.025 * PERS),
 ('L5-1: gross savings consensus needs at consensus comp', 170.0),
]
with open(RAW + r'\L4_dks_sizing.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['case', 'gross_$M', 'bp_of_FY27E_DSG_rev', '$_per_share_gross'])
    for name, m in cases:
        w.writerow([name, round(m, 1), round(m / BP, 1), round(m * EPS_PER_M, 3)])
        print(f'{name:55s} ${m:6.1f}M  {m/BP:5.1f}bp  ${m*EPS_PER_M:5.3f}/sh')
print('DSG personnel base FY27E ~$%.0fM' % PERS)

