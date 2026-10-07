"""P1: Bing News RSS + Google News RSS sweep for brand price increases / MSRP changes 2025-2026.
Rerun: python P1_newsrss.py [extra queries...] -> appends raw/P1_newsrss.csv (dedup by link). Prints new items.
No args = default brand x price query list.
"""
import requests, sys, csv, os, time, re, html
from urllib.parse import quote_plus
import xml.etree.ElementTree as ET
BASE = r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE"
OUT = os.path.join(BASE, 'raw', 'P1_newsrss.csv')
UA = {'User-Agent': 'Mozilla/5.0 (research; palazzolojustin@gmail.com)'}
BRANDS = ['Nike', 'Jordan Brand', 'Adidas', 'On Running', 'Hoka', 'Deckers', 'New Balance', 'Brooks Running', 'Asics',
          'Under Armour', 'The North Face', 'VF Corp', 'Columbia Sportswear', 'Yeti', 'Stanley cup', 'Titleist',
          'Acushnet', 'Callaway', 'TaylorMade', 'Bauer hockey', 'Wilson Sporting Goods', 'Rawlings', 'Easton bats',
          'Peloton', 'Garmin', 'Lululemon', 'Puma', 'Converse', 'Saucony', 'Skechers', 'Vans', 'Ping golf', 'Spalding',
          'Oakley', 'Carhartt', 'Hydro Flask']
DEFAULT = []
for b in BRANDS:
    DEFAULT.append(f'{b} "price increase" 2026')
    DEFAULT.append(f'{b} raise prices tariffs')


def bing(q):
    u = 'https://www.bing.com/news/search?q=' + quote_plus(q) + '&format=rss&count=50'
    r = requests.get(u, headers=UA, timeout=30); return parse(r.text, 'bing', q)


def gnews(q):
    u = 'https://news.google.com/rss/search?q=' + quote_plus(q) + '&hl=en-US&gl=US&ceid=US:en'
    r = requests.get(u, headers=UA, timeout=30); return parse(r.text, 'google', q)


def parse(txt, src, q):
    out = []
    try:
        root = ET.fromstring(txt)
    except Exception as e:
        return [(src, q, 'PARSEERR', '', '', str(e)[:80])]
    for it in root.iter('item'):
        g = lambda t: (it.findtext(t) or '').strip()
        desc = re.sub('<[^>]+>', ' ', html.unescape(g('description')))[:400]
        out.append((src, q, g('pubDate'), g('title'), g('link'), desc))
    return out


if __name__ == '__main__':
    qs = sys.argv[1:] or DEFAULT
    seen = set()
    if os.path.exists(OUT):
        for r in csv.reader(open(OUT, encoding='utf-8')):
            seen.add(r[4] if len(r) > 4 else '')
    f = open(OUT, 'a', newline='', encoding='utf-8'); w = csv.writer(f)
    for q in qs:
        for fn in (bing, gnews):
            try:
                rows = fn(q)
            except Exception as e:
                rows = [(fn.__name__, q, 'ERR', '', '', str(e)[:80])]
            n = 0
            for r in rows:
                if r[4] in seen and r[4]:
                    continue
                seen.add(r[4]); w.writerow(r); n += 1
            print(f'== {fn.__name__} {q}: {len(rows)} items, {n} new'); f.flush(); time.sleep(1.2)
