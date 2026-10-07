"""X09: summarise monthly Google Trends batches (raw/X09_gt_m_*.csv) into clean y/y comparisons that
exclude the contaminated Mar-22..Jun-27-2026 window.  Rerun: python X09_analyze_monthly.py
Output: raw/X09_gt_monthly_summary.csv
Periods: CY totals 2022-2025; Jan-Feb y/y; Jul-Sep y/y; Oct-Dec y/y; Apr-Jun (contaminated, shown for reference).
"""
import glob, os, pandas as pd
RAW = os.path.join(os.path.dirname(__file__), '..', 'raw')
res = []
for f in sorted(glob.glob(os.path.join(RAW, 'X09_gt_m_*.csv'))):
    b = os.path.basename(f)[9:-4]
    df = pd.read_csv(f, index_col=0, parse_dates=True)
    for t in df.columns:
        s = df[t]
        def tot(a, z):
            return s.loc[a:z].sum()
        r = dict(batch=b, term=t)
        for y in (2022, 2023, 2024, 2025):
            r[f'CY{y}'] = tot(f'{y}-01-01', f'{y}-12-31')
        r['CY25_vs_CY24%'] = (r['CY2025'] / r['CY2024'] - 1) * 100 if r['CY2024'] else None
        r['CY24_vs_CY23%'] = (r['CY2024'] / r['CY2023'] - 1) * 100 if r['CY2023'] else None
        for nm, a1, z1, a0, z0 in [('JanFeb', '2026-01-01', '2026-02-28', '2025-01-01', '2025-02-28'),
                                   ('JulSep', '2026-07-01', '2026-09-30', '2025-07-01', '2025-09-30'),
                                   ('OctDec25', '2025-10-01', '2025-12-31', '2024-10-01', '2024-12-31'),
                                   ('AprJun_CONTAM', '2026-04-01', '2026-06-30', '2025-04-01', '2025-06-30'),
                                   ('JulSep25', '2025-07-01', '2025-09-30', '2024-07-01', '2024-09-30')]:
            n, d = tot(a1, z1), tot(a0, z0)
            r[f'{nm}_now'], r[f'{nm}_prior'] = n, d
            r[f'{nm}_yoy%'] = (n / d - 1) * 100 if d else None
        res.append(r)
out = pd.DataFrame(res)
out.to_csv(os.path.join(RAW, 'X09_gt_monthly_summary.csv'), index=False)
pd.set_option('display.width', 250)
print(out[['batch', 'term', 'CY24_vs_CY23%', 'CY25_vs_CY24%', 'JulSep25_yoy%', 'OctDec25_yoy%', 'JanFeb_yoy%',
           'JulSep_now', 'JulSep_prior', 'JulSep_yoy%', 'AprJun_CONTAM_yoy%']].round(0).to_string())
