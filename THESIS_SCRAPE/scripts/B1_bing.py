"""B1: Bing web-search RSS (format=rss) + Bing News RSS + Google News RSS lead finder.
Rerun: python B1_bing.py web|bnews|gnews "<query>" ["<query2>" ...]  -> prints title | link | date | snippet; appends JSONL to raw/B1_search.jsonl
"""
import requests, sys, json, time, urllib.parse, html, re
import xml.etree.ElementTree as ET
H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36',
     'Accept-Language': 'en-US,en;q=0.9'}
OUT = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\B1_search.jsonl'
mode = sys.argv[1]
qs = []
for a in sys.argv[2:]:
    if a.startswith('@'):
        qs += [l.strip() for l in open(a[1:], encoding='utf-8') if l.strip() and not l.startswith('#')]
    else:
        qs.append(a)
for q in qs:
    qq = urllib.parse.quote(q)
    if mode == 'web':
        u = f'https://www.bing.com/search?q={qq}&format=rss&count=50'
    elif mode == 'bnews':
        u = f'https://www.bing.com/news/search?q={qq}&format=rss&count=50'
    else:
        u = f'https://news.google.com/rss/search?q={qq}&hl=en-US&gl=US&ceid=US:en'
    root = None
    for attempt in range(4):
        try:
            r = requests.get(u, headers=H, timeout=40)
            root = ET.fromstring(r.content)
            break
        except Exception as e:
            err = e
            time.sleep(6 * (attempt + 1))
    if root is None:
        print('ERR', q, err); continue
    items = root.findall('.//item')
    print(f'## [{mode}] {q} -> {len(items)}')
    with open(OUT, 'a', encoding='utf-8') as f:
        for it in items:
            d = {k: (it.findtext(k) or '') for k in ('title', 'link', 'pubDate', 'description')}
            d['description'] = re.sub('<[^>]+>', '', html.unescape(d['description']))[:300]
            d['q'] = q; d['mode'] = mode
            f.write(json.dumps(d) + '\n')
            print(' -', d['title'][:110], '|', d['link'][:150], '|', d['pubDate'][:16], '|', d['description'][:200])
    time.sleep(2)
