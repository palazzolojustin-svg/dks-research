"""B4: pair new DICK'S store numbers (>=1500, non-HoS and HoS) with old store numbers that dropped off the locator,
using the Wayback CDX census (B4_wayback_store_pages.csv) + live locator (H02_store_pages.json).
Output: raw/B4_reloc_pairs.csv (new store, first wayback capture, candidate replaced store(s) in same state within ~15 mi
by city name match, their last capture) and raw/B4_store_timeline.csv.
Rerun: python B4_reloc_pairs.py
"""
import csv, json, collections
R = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\\'
live = {}
for x in json.load(open(R + 'H02_store_pages.json', encoding='utf8')):
    try:
        live[int(x['storeno'])] = x
    except Exception:
        pass
wb = collections.defaultdict(lambda: {'first': '99999999', 'last': '0', 'n': 0, 'cities': set(), 'state': ''})
for r in csv.DictReader(open(R + 'B4_wayback_store_pages.csv', encoding='utf8')):
    n = int(r['storeno'])
    w = wb[n]
    w['first'] = min(w['first'], r['first']); w['last'] = max(w['last'], r['last']); w['n'] += int(r['captures'])
    w['cities'].add(r['city']); w['state'] = r['state']
rows = []
for n, w in wb.items():
    L = live.get(n)
    rows.append({'storeno': n, 'state': w['state'], 'cities': '|'.join(sorted(w['cities'])), 'first': w['first'], 'last': w['last'],
                 'captures': w['n'], 'live_2026_10': bool(L), 'live_name': L['ld_name'] if L else '', 'live_center': (L.get('h1') or '') if L else ''})
rows.sort(key=lambda r: r['storeno'])
with open(R + 'B4_store_timeline.csv', 'w', newline='', encoding='utf8') as f:
    wr = csv.DictWriter(f, fieldnames=list(rows[0].keys())); wr.writeheader(); wr.writerows(rows)
# dropped = in wayback, not live now, DSG range (<4000 excludes GGG 44xx, GG 5xxx? keep <2000)
dropped = [r for r in rows if not r['live_2026_10'] and r['storeno'] < 2000]
newr = [r for r in rows if r['storeno'] >= 1500 and r['storeno'] < 2000]
pairs = []
for nr in newr:
    cands = [d for d in dropped if d['state'] == nr['state'] and set(d['cities'].split('|')) & set(nr['cities'].split('|'))]
    pairs.append({**{k: nr[k] for k in ('storeno', 'state', 'cities', 'first', 'last', 'live_2026_10', 'live_name', 'live_center')},
                  'dropped_same_city': ';'.join(f"#{d['storeno']}({d['cities']},{d['first']}-{d['last']})" for d in cands)})
with open(R + 'B4_reloc_pairs.csv', 'w', newline='', encoding='utf8') as f:
    wr = csv.DictWriter(f, fieldnames=list(pairs[0].keys())); wr.writeheader(); wr.writerows(pairs)
print('wayback store numbers', len(rows), 'live', sum(r['live_2026_10'] for r in rows), 'dropped(<2000)', len(dropped))
for p in pairs:
    print(p['storeno'], p['state'], p['cities'][:30], p['first'], p['last'], 'LIVE' if p['live_2026_10'] else 'gone', p['live_name'][:22], '||', p['dropped_same_city'])
print('--- dropped list ---')
for d in dropped:
    print(d['storeno'], d['state'], d['cities'], d['first'], d['last'], d['captures'])
