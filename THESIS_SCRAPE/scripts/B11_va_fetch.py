"""B11: download Virginia quarterly taxable sales reports (locality x business classification) 2018-2026 from data.virginia.gov CKAN.
Rerun: python scripts/B11_va_fetch.py  -> raw/B11_cache/va/*.xls(x)"""
import requests, os, time
OUT = 'raw/B11_cache/va'; os.makedirs(OUT, exist_ok=True)
j = requests.get('https://data.virginia.gov/api/3/action/package_search?q=taxable%20sales%20data%20by%20locality&rows=60', timeout=60).json()
for p in j['result']['results']:
    if not p['name'].startswith('taxable-sales-data-by-locality'):
        continue
    for r in p['resources']:
        u = r['url']; fn = u.split('/')[-1]
        yr = ''.join(c for c in p['name'] if c.isdigit())
        if not yr or int(yr) < 2018: continue
        if not fn.lower().endswith(('.xls', '.xlsx')):
            print('skip', fn); continue
        dst = os.path.join(OUT, fn)
        if os.path.exists(dst): continue
        b = requests.get(u, timeout=120).content
        open(dst, 'wb').write(b); print(yr, fn, len(b)); time.sleep(0.5)
