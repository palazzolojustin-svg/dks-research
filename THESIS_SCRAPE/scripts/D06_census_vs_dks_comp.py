"""D06: map Census sporting-goods-store sales (NAICS 45111 NSA, MRTS) and NAICS 451 advance (SA) to DKS fiscal
quarters (Q1=Feb-Apr, Q2=May-Jul, Q3=Aug-Oct, Q4=Nov-Jan) and compare with DKS core comps.
Rerun after D06_census_fred.py: python THESIS_SCRAPE/scripts/D06_census_vs_dks_comp.py
Output: THESIS_SCRAPE/raw/D06_census_vs_dks_comp.csv
DKS comps from CORE_NOTES/00_CORE_DIGEST.md section 2c/2d (Q3FY22..Q2FY26).
"""
import pandas as pd, os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = pd.read_csv(os.path.join(BASE, 'raw', 'D06_census_fred.csv'), index_col=0, parse_dates=True)

def fq(ts):
    m, y = ts.month, ts.year
    # DKS fiscal year FYn ends ~Jan 31 of year n+1
    if m in (2, 3, 4): return f'FY{y}Q1'
    if m in (5, 6, 7): return f'FY{y}Q2'
    if m in (8, 9, 10): return f'FY{y}Q3'
    if m == 1: return f'FY{y-1}Q4'
    return f'FY{y}Q4'

d['fq'] = [fq(t) for t in d.index]
cols = ['MRTSSM45111USN', 'MRTSSM451USN', 'RSSGHBMS', 'RSXFS']
g = d.groupby('fq')[cols].agg(['sum', 'count'])
rows = []
for q in g.index:
    fy, qq = int(q[2:6]), q[-2:]
    prev = f'FY{fy-1}{qq}'
    if prev not in g.index: continue
    r = {'fq': q}
    for c in cols:
        n, n0 = g.loc[q, (c, 'count')], g.loc[prev, (c, 'count')]
        if n == 3 and n0 == 3:
            r[c + '_yy'] = (g.loc[q, (c, 'sum')] / g.loc[prev, (c, 'sum')] - 1) * 100
        elif n > 0:
            # partial quarter: compare same months
            months = d[d.fq == q].dropna(subset=[c]).index
            prevm = [m - pd.DateOffset(years=1) for m in months]
            if not all(p in d.index for p in prevm): continue
            r[c + '_yy'] = (d.loc[months, c].sum() / d.loc[prevm, c].sum() - 1) * 100
            r[c + '_note'] = f'partial {len(months)}m'
    rows.append(r)
q = pd.DataFrame(rows).set_index('fq')
dks = {'FY2022Q3': 6.5, 'FY2022Q4': 5.3, 'FY2023Q1': 3.4, 'FY2023Q2': 1.8, 'FY2023Q3': 1.7, 'FY2023Q4': 2.8,
       'FY2024Q1': 5.3, 'FY2024Q2': 4.5, 'FY2024Q3': 4.2, 'FY2024Q4': 6.4, 'FY2025Q1': 4.5, 'FY2025Q2': 5.0,
       'FY2025Q3': 5.7, 'FY2025Q4': 3.1, 'FY2026Q1': 6.0, 'FY2026Q2': 4.9, 'FY2026Q3': 1.69}  # FY26Q3 = consensus
q['DKS_comp'] = pd.Series(dks)
q['gap_vs_45111'] = q['DKS_comp'] - q['MRTSSM45111USN_yy']
q['gap_vs_451adv'] = q['DKS_comp'] - q['RSSGHBMS_yy']
q = q[q.index >= 'FY2021Q1']
q.to_csv(os.path.join(BASE, 'raw', 'D06_census_vs_dks_comp.csv'))
pd.set_option('display.width', 250)
print(q.round(2).to_string())
