"""B6: SEC EDGAR full-text search for DICK'S x store-tech vendors (and vendor filings naming DICK'S).
Rerun: python B6_edgar_fts.py  -> raw/B6_edgar_fts.json ; prints hits (entity, form, date, file).
"""
import requests, json, time
H = {'User-Agent': 'DKS research palazzolojustin@gmail.com'}
Q = ['"Dick\'s Sporting Goods" RFID', '"Dick\'s Sporting Goods" "workforce management"', '"Dick\'s Sporting Goods" "self-checkout"',
     '"Dick\'s Sporting Goods" Legion', '"Dick\'s Sporting Goods" "electronic shelf"', '"Dick\'s Sporting Goods" "labor management"',
     '"DICK\'S Sporting Goods" "store labor"', '"store operating model" "Dick\'s"', '"Dick\'s Sporting Goods" "customer" "RFID"',
     '"Dick\'s Sporting Goods" Zebra', '"Dick\'s Sporting Goods" "handheld"', '"Dick\'s Sporting Goods" "scheduling"']
out = {}
for q in Q:
    u = 'https://efts.sec.gov/LATEST/search-index?q=' + requests.utils.quote(q) + '&dateRange=custom&startdt=2019-01-01&enddt=2026-10-07'
    try:
        r = requests.get(u, headers=H, timeout=40); d = r.json()
    except Exception as e:
        print('ERR', q, e); continue
    hits = d.get('hits', {}).get('hits', [])
    tot = d.get('hits', {}).get('total', {}).get('value')
    print('==', q, tot)
    out[q] = []
    for h in hits[:40]:
        s = h['_source']
        rec = (s.get('display_names', [''])[0][:50], s.get('form'), s.get('file_date'), h['_id'])
        out[q].append(rec); print('   ', rec)
    time.sleep(0.6)
json.dump(out, open(r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\B6_edgar_fts.json', 'w'), indent=1)
