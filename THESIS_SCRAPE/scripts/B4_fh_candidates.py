"""B4: candidate Field House / next-gen store list from the DKS locator scrape (H02_store_pages.json).
Logic: DKS assigns NEW store numbers to relocations/new boxes; store numbers >=1560 that are not HoS-branded are
(mostly) next-gen 50K / Field House boxes opened 2023-2026. Writes raw/B4_fh_candidates.csv and city query files.
Rerun: python B4_fh_candidates.py
"""
import json, csv
R = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\\'
d = json.load(open(R + 'H02_store_pages.json', encoding='utf8'))
rows = []
for x in d:
    try:
        n = int(x['storeno'])
    except Exception:
        continue
    if 1500 <= n < 1800 and 'House of Sport' not in x['ld_name'] and x['city']:
        rows.append({'tier': 1 if n >= 1560 else 2, 'storeno': n, 'city': x['city'], 'state': x['state'], 'center': x.get('h1', '').replace("DICK'S Sporting Goods", '').strip(),
                     'address': x['address1'], 'lat': x['latitude'], 'lon': x['longitude']})
rows.sort(key=lambda r: r['storeno'])
with open(R + 'B4_fh_candidates.csv', 'w', newline='', encoding='utf8') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
qs = []
for r in rows:
    qs.append(f'"Dick\'s Sporting Goods" {r["city"]} new store')
    if r['center']:
        qs.append(f'"Dick\'s" "{r["center"].title()}" {r["city"]}')
open(R + 'B4_city_queries.txt', 'w', encoding='utf8').write('\n'.join(qs))
for r in rows:
    print(r['storeno'], r['city'], r['state'], '|', r['center'], '|', r['address'])
print(len(rows), 'candidates;', len(qs), 'queries')

