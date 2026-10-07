"""B6 wave 3: Google News RSS + Bing News RSS for DKS store-tech vendor queries, plus Wayback CDX for given URLs.
Rerun: python B6_w3_rss.py  -> raw/B6_w3_rss.csv (appends) ; edit QUERIES / CDX below.
"""
import requests, urllib.parse, csv, sys, time
import xml.etree.ElementTree as ET
RAW = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw'
QUERIES = sys.argv[1:] or [
    '"Dick\'s Sporting Goods" RFID',
    '"Dick\'s Sporting Goods" RFID suppliers tagging',
    '"Dick\'s Sporting Goods" Legion',
    '"Dick\'s Sporting Goods" Zebra',
    '"Dick\'s Sporting Goods" self-checkout',
    '"Dick\'s Sporting Goods" store associates app technology',
    '"Dick\'s Sporting Goods" workforce scheduling AI',
    '"Dick\'s Sporting Goods" chief technology officer stores',
]
out = open(RAW + r'\B6_w3_rss.csv', 'a', newline='', encoding='utf-8')
w = csv.writer(out)
for q in QUERIES:
    for src, url in [('gnews', 'https://news.google.com/rss/search?q=' + urllib.parse.quote(q) + '&hl=en-US&gl=US&ceid=US:en'),
                     ('bing', 'https://www.bing.com/news/search?q=' + urllib.parse.quote(q) + '&format=rss')]:
        try:
            r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=30)
            items = ET.fromstring(r.content).findall('.//item')
        except Exception as e:
            print('ERR', src, q, e); continue
        print('==', src, q, len(items))
        for it in items[:25]:
            row = [src, q, (it.findtext('pubDate') or '')[:16], it.findtext('title') or '', it.findtext('link') or '']
            w.writerow(row)
            print('  ', row[2], '|', row[3][:150])
        time.sleep(1)
out.close()
