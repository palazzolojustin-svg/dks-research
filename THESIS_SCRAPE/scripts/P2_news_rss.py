"""P2_news_rss.py: Google News + Bing News RSS queries for DKS pricing / promo / price-check coverage. Output raw\\P2_news_rss.csv
Rerun: python P2_news_rss.py
"""
import requests, csv, time, urllib.parse
from bs4 import BeautifulSoup
H = {'User-Agent': 'Mozilla/5.0 (research; palazzolojustin@gmail.com)'}
QS = [
    '"Dick\'s Sporting Goods" prices tariffs 2026', '"Dick\'s Sporting Goods" raising prices', '"Dick\'s" price increase Nike shoes 2026',
    '"Dick\'s Sporting Goods" promotions discount 2026', '"Dick\'s Sporting Goods" price match', '"Dick\'s Sporting Goods" markdowns',
    'sneaker prices tariffs 2026 retail', 'running shoe price increase 2026', 'Nike price increase 2026', 'Hoka price increase 2026',
    'On Running price increase 2026', 'Yeti price increase tariffs', 'Stanley cup price increase', 'golf ball price increase 2026 Pro V1',
    'baseball bat price increase tariffs', '"Dick\'s Sporting Goods" "average ticket"', '"Dick\'s Sporting Goods" "price investment"',
    '"Dick\'s Sporting Goods" "promotional" September 2026', '"sporting goods" prices CPI September 2026', 'athletic footwear promotions September 2026',
]
rows = []
for q in QS:
    for src, url in [('google', 'https://news.google.com/rss/search?q=%s&hl=en-US&gl=US&ceid=US:en' % urllib.parse.quote(q)),
                     ('bing', 'https://www.bing.com/news/search?q=%s&format=rss' % urllib.parse.quote(q))]:
        try:
            r = requests.get(url, headers=H, timeout=60)
            s = BeautifulSoup(r.content, 'xml')
            for it in s.find_all('item')[:40]:
                rows.append([q, src, it.title.text if it.title else '', it.pubDate.text if it.pubDate else '', it.link.text if it.link else '',
                             (it.description.text if it.description else '')[:400]])
        except Exception as e:
            print(q, src, 'ERR', e)
        time.sleep(1.5)
with open(r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\P2_news_rss.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['query', 'src', 'title', 'date', 'link', 'desc']); w.writerows(rows)
print(len(rows))
