"""L5: Pull BLS CES wage/hours/employment series for retail sub-industries relevant to DKS store labor.
Rerun: python THESIS_SCRAPE\\scripts\\L5_bls_wages.py  -> writes THESIS_SCRAPE\\raw\\L5_bls_ces.csv (long format)
BLS public API v2 without key (limit ~25 queries/day, 10 yrs/query). Series:
  CES industry codes (NAICS 2022 basis): 42000000 retail trade; 42459000 sporting goods/hobby/musical/book/misc retailers;
  42459110 sporting goods retailers; 42455000 general merchandise retailers; 42455200? (warehouse clubs/supercenters/other GM)
  data types: 03 AHE all employees, 08 AHE prod&nonsupervisory, 02 avg weekly hours all, 07 avg weekly hours P&NS, 01 employment (000), 56 aggregate weekly hours index? (16 = index agg weekly hrs all)
"""
import requests, json, csv, os
ROOT = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE'
inds = {'42000000': 'Retail trade', '42459000': 'Sporting goods/hobby/music/book/misc retailers',
        '42459110': 'Sporting goods retailers', '42455000': 'General merchandise retailers'}
dts = {'03': 'AHE all emp', '08': 'AHE P&NS', '02': 'AWH all emp', '07': 'AWH P&NS', '01': 'Employment (000)'}
series = [f'CEU{i}{d}' for i in inds for d in dts]
rows = []
for chunk in [series[i:i+25] for i in range(0, len(series), 25)]:
    r = requests.post('https://api.bls.gov/publicAPI/v2/timeseries/data/',
                      json={'seriesid': chunk, 'startyear': '2019', 'endyear': '2026'},
                      headers={'Content-type': 'application/json'}, timeout=60)
    j = r.json()
    print(j.get('status'), j.get('message'))
    for s in j.get('Results', {}).get('series', []):
        sid = s['seriesID']
        for d in s['data']:
            if d['period'].startswith('M') and d['period'] != 'M13':
                rows.append(dict(series=sid, industry=inds.get(sid[3:11]), dtype=dts.get(sid[11:]), year=int(d['year']),
                                 month=int(d['period'][1:]), value=d['value'], footnote=';'.join(f.get('text', '') for f in d.get('footnotes', []) if f)))
        print(sid, len(s['data']))
with open(os.path.join(ROOT, 'raw', 'L5_bls_ces.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['series', 'industry', 'dtype', 'year', 'month', 'value', 'footnote']); w.writeheader(); w.writerows(rows)
print(len(rows), 'rows')
