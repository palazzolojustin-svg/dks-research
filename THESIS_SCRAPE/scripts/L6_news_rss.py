"""L6: Google News + Bing News RSS sweep for DKS / Golf Galaxy / Foot Locker layoffs, WARN notices,
HQ / DC job cuts, store-manager restructuring (2025-2026).
Rerun: python THESIS_SCRAPE\\scripts\\L6_news_rss.py
Output: THESIS_SCRAPE\\raw\\L6_news_rss.json (deduped items: query, source, title, date, link, snippet)
"""
import requests, time, json, os, re, html
from urllib.parse import quote_plus
from xml.etree import ElementTree as ET
H = {'User-Agent': 'Mozilla/5.0 (research; palazzolojustin@gmail.com)'}
RAW = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw'
QUERIES = [
    '"Dick\'s Sporting Goods" layoffs', '"Dick\'s Sporting Goods" layoffs 2026', '"Dick\'s Sporting Goods" WARN notice',
    '"Dick\'s Sporting Goods" job cuts', '"Dick\'s Sporting Goods" eliminates positions', '"Dick\'s Sporting Goods" corporate layoffs Coraopolis',
    '"Dick\'s Sporting Goods" store managers restructuring', '"Dick\'s Sporting Goods" store leadership changes', '"Dick\'s Sporting Goods" "store operating model"',
    '"Dick\'s Sporting Goods" distribution center layoffs', '"Dick\'s Sporting Goods" distribution center closing', '"Dick\'s Sporting Goods" severance',
    '"Golf Galaxy" layoffs', '"Going Going Gone" Dick\'s closing', '"Dick\'s" Coraopolis layoffs', 'DKS layoffs headquarters',
    '"Foot Locker" layoffs 2026', '"Foot Locker" headquarters layoffs Dick\'s', '"Foot Locker" WARN notice 2026', '"Foot Locker" St. Petersburg layoffs',
    '"Foot Locker" Wausau layoffs', '"Foot Locker" corporate job cuts Dick\'s integration', '"Foot Locker" New York headquarters Dick\'s',
    '"Dick\'s Sporting Goods" "WARN"', '"Dick\'s Sporting Goods" laid off employees', '"Dick\'s Sporting Goods" restructuring jobs',
    '"Dick\'s Sporting Goods" Conklin distribution center', '"Dick\'s Sporting Goods" Fort Worth distribution center', '"Dick\'s Sporting Goods" Smithton distribution',
    '"Dick\'s Sporting Goods" store closing employees 2026', '"Dick\'s Sporting Goods" GameChanger layoffs', '"Dick\'s Sporting Goods" tech layoffs',
    '"Dick\'s Sporting Goods" "store teammates" new roles', '"Dick\'s Sporting Goods" assistant store manager eliminated',
]

def gnews(q):
    u = f'https://news.google.com/rss/search?q={quote_plus(q)}&hl=en-US&gl=US&ceid=US:en'
    return u
def bing(q):
    return f'https://www.bing.com/news/search?q={quote_plus(q)}&format=rss'

def fetch(u):
    for i in range(3):
        try:
            r = requests.get(u, headers=H, timeout=40)
            if r.status_code == 200 and '<rss' in r.text[:500]:
                return r.text
            return None
        except Exception:
            time.sleep(2)

items = {}
for q in QUERIES:
    for src, fn in (('gnews', gnews), ('bing', bing)):
        t = fetch(fn(q))
        if not t:
            print('fail', src, q); continue
        try:
            root = ET.fromstring(t)
        except Exception:
            print('parse fail', src, q); continue
        for it in root.iter('item'):
            title = (it.findtext('title') or '').strip()
            link = (it.findtext('link') or '').strip()
            date = (it.findtext('pubDate') or '').strip()
            desc = re.sub('<[^>]+>', ' ', html.unescape(it.findtext('description') or ''))[:400]
            key = title.lower()[:120]
            if key not in items:
                items[key] = dict(query=q, src=src, title=title, date=date, link=link, snippet=desc.strip())
        time.sleep(1)
json.dump(list(items.values()), open(os.path.join(RAW, 'L6_news_rss.json'), 'w', encoding='utf-8'), indent=1)
print('items', len(items))
