"""D06: App Store rating-count & chart-rank time series from Wayback Machine snapshots of public apps.apple.com pages,
plus today's live value from the public iTunes lookup API.
Rerun: python THESIS_SCRAPE/scripts/D06_appstore_wayback.py
Output: THESIS_SCRAPE/raw/D06_appstore_wayback.csv
Apps: DICK'S (556653197), Academy (1572699554), Foot Locker (934030757), GameChanger (1308415878).
Method: CDX list of 200-status snapshots (collapsed to 1 per month), fetch raw snapshot (id_ suffix), regex for
"N Ratings"/ratingCount JSON and "#N in <Category>".
"""
import re, os, time, json, requests, csv
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPS = {'DKS': ('dicks-sporting-goods', 556653197), 'ASO': ('academy-sports-outdoors', 1572699554),
        'FL': ('foot-locker-shop-releases', 934030757), 'GC': ('gamechanger', 1308415878)}
H = {'User-Agent': 'Mozilla/5.0 (research; contact via wayback etiquette)'}
rows = []

def parse(t):
    rc = None
    m = re.search(r'"ratingCount"\s*:\s*"?([\d.]+)', t) or re.search(r'"userRatingCount"\s*:\s*([\d]+)', t)
    if m: rc = float(m.group(1))
    m2 = re.search(r'([\d.,]+)\s*([KM]?)\s*Ratings', t)
    txt = None
    if m2:
        v = float(m2.group(1).replace(',', '')); mult = {'K': 1e3, 'M': 1e6}.get(m2.group(2), 1); txt = v * mult
    rank = re.search(r'#(\d+)\s+in\s+([A-Za-z &;]+)', t)
    return rc, txt, (rank.group(1) + ' ' + rank.group(2).strip()) if rank else None

for k, (slug, aid) in APPS.items():
    # live
    try:
        j = requests.get('https://itunes.apple.com/lookup', params={'id': aid, 'country': 'us'}, timeout=30).json()['results'][0]
        rows.append([k, 'live-2026-10-07', j.get('userRatingCount'), None, None, 'itunes lookup'])
    except Exception as e:
        print('live fail', k, e)
    for pat in [f'apps.apple.com/us/app/{slug}/id{aid}', f'apps.apple.com/us/app/id{aid}']:
        try:
            cdx = requests.get('https://web.archive.org/cdx/search/cdx', params={'url': pat, 'output': 'json', 'from': '2023',
                               'filter': 'statuscode:200', 'collapse': 'timestamp:6'}, timeout=60, headers=H).json()
        except Exception as e:
            print('cdx fail', k, e); continue
        for rec in cdx[1:]:
            ts = rec[1]
            u = f'https://web.archive.org/web/{ts}id_/{rec[2]}'
            try:
                t = requests.get(u, timeout=60, headers=H).text
            except Exception as e:
                print('snap fail', u, e); continue
            rc, txt, rank = parse(t)
            rows.append([k, ts, rc, txt, rank, pat])
            print(k, ts, rc, txt, rank)
            time.sleep(4)
with open(os.path.join(BASE, 'raw', 'D06_appstore_wayback.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['app', 'timestamp', 'ratingCount_json', 'ratings_text', 'chart_rank', 'source']); w.writerows(rows)
print('saved', len(rows))

