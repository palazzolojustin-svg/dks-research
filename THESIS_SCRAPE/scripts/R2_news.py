"""R2: Google News RSS (fallback Bing News RSS) query helper. Usage: python R2_news.py "query 1" "query 2" ...
Appends results to raw/R2_news.txt
"""
import requests, sys, xml.etree.ElementTree as ET, urllib.parse, time
R = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\\'
H = {'User-Agent': 'Mozilla/5.0 (research script; palazzolojustin@gmail.com)'}
out = open(R + 'R2_news.txt', 'a', encoding='utf-8')
for q in sys.argv[1:]:
    for name, url in [('G', 'https://news.google.com/rss/search?q=' + urllib.parse.quote(q) + '&hl=en-US&gl=US&ceid=US:en'),
                      ('B', 'https://www.bing.com/news/search?q=' + urllib.parse.quote(q) + '&format=rss')]:
        try:
            r = requests.get(url, headers=H, timeout=30)
            items = ET.fromstring(r.content).findall('.//item')
        except Exception as e:
            print(name, q, 'ERR', e); continue
        print(f'=== [{name}] {q} ({len(items)})'); out.write(f'=== [{name}] {q} ({len(items)})\n')
        for it in items[:25]:
            t = it.findtext('title'); d = it.findtext('pubDate'); l = it.findtext('link')
            s = f'{d} | {t} | {l}'
            print(s[:300]); out.write(s + '\n')
        time.sleep(1)
