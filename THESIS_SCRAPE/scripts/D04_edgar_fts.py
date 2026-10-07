"""D04: EDGAR full-text search for vendor 10-K/10-Q/20-F/6-K filings that name DICK'S Sporting Goods (customer concentration).
Rerun: python D04_edgar_fts.py  -> raw/D04_edgar_fts_hits.json + printed list of (company, form, date, url)
Uses the public efts.sec.gov JSON endpoint (SEC fair-access UA header)."""
import requests, json, time
H = {'User-Agent': 'DKS research palazzolojustin@gmail.com', 'Accept': 'application/json'}
OUT = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\D04_edgar_fts_hits.json'
queries = ['"Dick\'s Sporting Goods" "net sales"', '"Dick\'s Sporting Goods" "largest customer"',
           '"Dick\'s Sporting Goods" "% of" customer', '"DICK\'S Sporting Goods" "accounted for"']
hits = {}
for q in queries:
    for frm in ['10-K', '20-F', '10-Q']:
        start = 0
        while start < 400:
            p = {'q': q, 'forms': frm, 'dateRange': 'custom', 'startdt': '2022-01-01', 'enddt': '2026-10-07', 'from': start}
            try:
                r = requests.get('https://efts.sec.gov/LATEST/search-index', params=p, headers=H, timeout=60)
                d = r.json()
            except Exception as e:
                print('ERR', q, frm, e); break
            hh = d.get('hits', {}).get('hits', [])
            for x in hh:
                s = x['_source']
                key = x['_id']
                hits[key] = {'name': s.get('display_names'), 'form': s.get('form'), 'date': s.get('file_date'),
                             'adsh': s.get('adsh'), 'ciks': s.get('ciks'), 'id': key, 'q': q}
            total = d.get('hits', {}).get('total', {}).get('value', 0)
            start += 100
            if start >= total:
                break
            time.sleep(0.3)
        time.sleep(0.3)
json.dump(hits, open(OUT, 'w'), indent=1)
from collections import Counter
names = Counter()
for v in hits.values():
    names[(v['name'][0] if v['name'] else '?')] += 1
for n, c in names.most_common(200):
    print(c, n)
