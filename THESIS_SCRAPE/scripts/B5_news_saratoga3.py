"""B5: Google/Bing News RSS search to identify the cause of the Saratoga County NY sporting-goods step-up (Jun-2025+).
Rerun: python scripts/B5_news_saratoga3.py [query ...]  -> prints titles; output tee'd to raw/B5_saratoga_news3.txt
"""
import requests, re, html, urllib.parse, time, sys
H = {'User-Agent': 'Mozilla/5.0 (research; palazzolojustin@gmail.com)'}
qs = sys.argv[1:] or ['"Wilton Mall" 2025', '"Wilton Mall" Dick\'s', 'Dick\'s "Field House" Wilton', 'Saratoga "Field House" Dick\'s',
      'Clifton Park sporting goods store opening 2025', 'Saratoga "Golf Galaxy"', '"Wilton Mall" Bon-Ton space', 'Saratoga Springs store opening June 2025 sporting',
      'Malta NY new store 2025', 'Saratoga County hockey store OR ski shop opens 2025']
for q in qs:
    for eng, u in [('g', 'https://news.google.com/rss/search?q=' + urllib.parse.quote(q) + '&hl=en-US&gl=US&ceid=US:en'),
                   ('b', 'https://www.bing.com/news/search?q=' + urllib.parse.quote(q) + '&format=rss')]:
        try:
            t = requests.get(u, headers=H, timeout=30).text
        except Exception as e:
            print('ERR', e); continue
        items = re.findall(r'<item>.*?<title>(.*?)</title>.*?<link>(.*?)</link>.*?<pubDate>(.*?)</pubDate>', t, re.S)
        print('==', eng, q, len(items), flush=True)
        for ti, l, d in items[:10]:
            print('  ', d[5:16], '|', html.unescape(ti)[:140], '|', l[:160], flush=True)
        time.sleep(1)
