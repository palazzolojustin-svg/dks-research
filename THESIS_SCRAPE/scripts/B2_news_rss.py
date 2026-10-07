"""B2: Google News + Bing News RSS sweep for foot-traffic datapoints on DICK'S / House of Sport / Foot Locker.
Writes raw/B2_news_rss.json (dedup by link) and prints title/date/source. Rerun: python B2_news_rss.py
"""
import requests, re, json, os, time, html
from urllib.parse import quote
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTF = os.path.join(BASE, 'raw', 'B2_news_rss.json')
H = {'User-Agent': 'Mozilla/5.0 (research script; palazzolojustin@gmail.com)'}
Q = [
    '"Placer.ai" "Dick\'s Sporting Goods"', '"Placer.ai" "House of Sport"', '"House of Sport" "foot traffic"',
    '"House of Sport" visits mall', '"Dick\'s" "foot traffic" 2026', '"Dick\'s Sporting Goods" "visits" Placer 2026',
    '"Foot Locker" "Placer.ai" 2026', '"Foot Locker" "foot traffic" 2026', '"Advan" "Dick\'s"', '"Dick\'s" "store visits" 2026',
    '"House of Sport" "visits" 2026', '"Dick\'s Sporting Goods" foot traffic September 2026', '"Dick\'s Sporting Goods" foot traffic August 2026',
    '"sporting goods" "foot traffic" 2026 Placer', '"Dick\'s" traffic "Placer" analyst', '"House of Sport" "traffic" analyst note',
    '"Dick\'s" "same-store visits"', '"House of Sport" Placer visits per location', 'Chernofsky "Dick\'s"', '"Dick\'s House of Sport" visitors',
]
res = {}
if os.path.exists(OUTF):
    res = json.load(open(OUTF, encoding='utf-8'))


def items(xml):
    for it in re.findall(r'<item>(.*?)</item>', xml, re.S):
        g = lambda tag: html.unescape(re.sub(r'<!\[CDATA\[|\]\]>', '', (re.search(rf'<{tag}[^>]*>(.*?)</{tag}>', it, re.S) or [None, ''])[1])).strip()
        yield {'title': g('title'), 'link': g('link'), 'date': g('pubDate'), 'src': g('source'), 'desc': re.sub('<[^>]+>', ' ', g('description'))[:400]}


for q in Q:
    for name, url in [('g', f'https://news.google.com/rss/search?q={quote(q)}&hl=en-US&gl=US&ceid=US:en'),
                      ('b', f'https://www.bing.com/news/search?q={quote(q)}&format=rss')]:
        try:
            r = requests.get(url, headers=H, timeout=40)
            n = 0
            for it in items(r.text):
                if it['link'] not in res:
                    it['q'] = q; it['engine'] = name
                    res[it['link']] = it; n += 1
            print(name, q, r.status_code, n)
        except Exception as e:
            print('ERR', name, q, e)
        time.sleep(1.5)
json.dump(res, open(OUTF, 'w', encoding='utf-8'), indent=1)
for it in sorted(res.values(), key=lambda x: x['date']):
    print(it['date'][:16], '|', it['src'][:25], '|', it['title'][:140])
