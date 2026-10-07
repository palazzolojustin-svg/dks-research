"""R2: QCEW county pulls for other NAICS (default 459120 hobby/toy/game, 459140 musical instruments) for NY counties, 2022Q1-2026Q1.
Rerun: python R2_qcew_other.py -> raw/R2_qcew_other.csv
"""
import requests, pandas as pd, io, time
R = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\\'
H = {'User-Agent': 'research palazzolojustin@gmail.com'}
out = []
for ind in ['459120', '459140']:
    for y in range(2022, 2027):
        for q in range(1, 5):
            if y == 2026 and q > 1: break
            u = f'https://data.bls.gov/cew/data/api/{y}/{q}/industry/{ind}.csv'
            try:
                t = requests.get(u, headers=H, timeout=120).text
                d = pd.read_csv(io.StringIO(t), dtype={'area_fips': str})
                d = d[d.area_fips.str.startswith('36') & (d.own_code == 5)]
                out.append(d[['area_fips', 'year', 'qtr', 'industry_code', 'qtrly_estabs', 'month3_emplvl', 'total_qtrly_wages', 'disclosure_code']])
                print(ind, y, q, len(d))
            except Exception as e:
                print('ERR', u, e)
            time.sleep(0.5)
df = pd.concat(out)
df.to_csv(R + 'R2_qcew_other.csv', index=False)
for f in ['36071', '36113', '36063', '36055']:
    print('==', f); print(df[df.area_fips == f].sort_values(['industry_code', 'year', 'qtr']).to_string(index=False))
