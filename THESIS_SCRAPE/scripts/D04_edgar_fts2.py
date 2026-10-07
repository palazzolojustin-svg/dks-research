"""D04: list every filer whose 10-K / 20-F (2023-01-01..2026-10-07) contains the phrase "Dick's Sporting Goods".
Rerun: python D04_edgar_fts2.py -> raw/D04_edgar_fts_filers.json"""
import requests, json, time
from collections import defaultdict
H = {'User-Agent': 'DKS research palazzolojustin@gmail.com', 'Accept': 'application/json'}
OUT = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\D04_edgar_fts_filers.json'
filers = defaultdict(list)
for frm in ['10-K', '20-F']:
    start = 0
    while True:
        p = {'q': '"Dick\'s Sporting Goods"', 'forms': frm, 'dateRange': 'custom', 'startdt': '2023-01-01', 'enddt': '2026-10-07', 'from': start}
        r = requests.get('https://efts.sec.gov/LATEST/search-index', params=p, headers=H, timeout=60)
        d = r.json()
        hh = d.get('hits', {}).get('hits', [])
        if not hh:
            break
        for x in hh:
            s = x['_source']
            nm = s['display_names'][0] if s.get('display_names') else '?'
            filers[nm].append((s.get('form'), s.get('file_date'), x['_id']))
        total = d['hits']['total']['value']
        start += len(hh)
        print(frm, start, total)
        if start >= total or start >= 2000:
            break
        time.sleep(0.25)
json.dump(filers, open(OUT, 'w'), indent=1)
for nm in sorted(filers, key=lambda k: -len(filers[k])):
    print(len(filers[nm]), nm, sorted(set(f[1][:4] for f in filers[nm])))
