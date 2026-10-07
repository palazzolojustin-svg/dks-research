"""B4: Google News RSS sweep for DICK'S Field House / next-gen / relocated-store openings, 2023-2026.
Runs each query over half-year windows (after:/before:) to get past the 100-item cap per feed.
Rerun: python B4_gnews.py  -> THESIS_SCRAPE/raw/B4_gnews.json (dict query|window -> items) and B4_gnews_titles.txt
"""
import json, time, re, html, requests, itertools
from urllib.parse import quote
import xml.etree.ElementTree as ET

H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0 Safari/537.36'}
OUT = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\B4_gnews'
Q = [
    '"Dick\'s" "Field House"',
    '"Dick\'s Sporting Goods" "next generation" store',
    '"Dick\'s Sporting Goods" "next-gen" store',
    '"Dick\'s Sporting Goods" relocating',
    '"Dick\'s Sporting Goods" relocate larger store',
    '"Dick\'s Sporting Goods" "square-foot" new store',
    '"Dick\'s Sporting Goods" "grand opening"',
    '"Dick\'s Sporting Goods" moving new location',
    '"Dick\'s Sporting Goods" "new store" opening',
    '"Dick\'s Sporting Goods" "batting cage" new store',
    '"Dick\'s Sporting Goods" Sears building',
    '"Dick\'s Sporting Goods" "former" store opens',
]
W = [('2023-01-01', '2023-07-01'), ('2023-07-01', '2024-01-01'), ('2024-01-01', '2024-07-01'), ('2024-07-01', '2025-01-01'),
     ('2025-01-01', '2025-07-01'), ('2025-07-01', '2026-01-01'), ('2026-01-01', '2026-07-01'), ('2026-07-01', '2026-10-08')]
res = {}
titles = {}
for q, (a, b) in itertools.product(Q, W):
    url = f'https://news.google.com/rss/search?q={quote(q + f" after:{a} before:{b}")}&hl=en-US&gl=US&ceid=US:en'
    for att in range(3):
        try:
            r = requests.get(url, headers=H, timeout=20)
            if r.status_code == 200:
                break
            print('status', r.status_code, flush=True)
        except Exception as e:
            r = None
        time.sleep(5 * (att + 1))
    if r is None or r.status_code != 200:
        print('FAIL', q, a, r.status_code if r else None); continue
    root = ET.fromstring(r.content)
    items = []
    for it in root.iter('item'):
        t = it.findtext('title'); l = it.findtext('link'); d = it.findtext('pubDate'); s = it.findtext('source')
        items.append({'title': t, 'link': l, 'date': d, 'source': s})
        titles.setdefault(t, (d, s, l))
    res[f'{q}|{a}'] = items
    json.dump(res, open(OUT + '.json', 'w', encoding='utf8'))
    print(len(items), q, a, flush=True)
    time.sleep(1.5)
json.dump(res, open(OUT + '.json', 'w', encoding='utf8'), indent=1)
from email.utils import parsedate_to_datetime
rows = []
for t, (d, s, l) in titles.items():
    try:
        dd = parsedate_to_datetime(d).strftime('%Y-%m-%d')
    except Exception:
        dd = d
    rows.append((dd, t))
rows.sort(reverse=True)
with open(OUT + '_titles.txt', 'w', encoding='utf8') as f:
    for dd, t in rows:
        f.write(f'{dd} | {t}\n')
print('unique titles', len(rows))

