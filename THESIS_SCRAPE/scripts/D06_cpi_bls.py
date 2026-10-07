"""D06: CPI price indexes relevant to DKS from the public BLS API v1 (no key; 25 req/day limit) to deflate Census sales.
Rerun: python THESIS_SCRAPE/scripts/D06_cpi_bls.py
Series: CUUR0000SERC sporting goods; CUUR0000SERC01 sports vehicles incl bikes; CUUR0000SERC02 sports equipment;
        CUUR0000SEAE footwear; CUUR0000SAA apparel. Output raw/D06_cpi_bls.csv with y/y %.
"""
import requests, json, os, csv
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = ['CUUR0000SERC', 'CUUR0000SERC02', 'CUUR0000SEAE', 'CUUR0000SAA']
r = requests.post('https://api.bls.gov/publicAPI/v1/timeseries/data/', json={'seriesid': S, 'startyear': '2024', 'endyear': '2026'},
                  timeout=60)
j = r.json()
print(j.get('status'), j.get('message'))
rows = []
for s in j['Results']['series']:
    d = {(x['year'], x['period']): float(x['value']) for x in s['data'] if x['period'].startswith('M') and x['value'] not in ('-',)}
    for (y, p), v in sorted(d.items()):
        prev = d.get((str(int(y) - 1), p))
        rows.append([s['seriesID'], f'{y}-{p[1:]}', v, round((v / prev - 1) * 100, 2) if prev else None])
with open(os.path.join(BASE, 'raw', 'D06_cpi_bls.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['series', 'month', 'index', 'yoy_pct']); w.writerows(rows)
for r_ in rows:
    if r_[1] >= '2025-07': print(r_)
