"""L6: Bing News RSS query -> title | date | decoded publisher URL | snippet.
Usage: python L6_bing.py "query 1" "query 2" ...   Appends to THESIS_SCRAPE\\raw\\L6_bing.jsonl
"""
import requests, sys, re, html, json, time
from urllib.parse import quote_plus, urlparse, parse_qs
from xml.etree import ElementTree as ET
H = {'User-Agent': 'Mozilla/5.0 (research; palazzolojustin@gmail.com)'}
out = open(r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\L6_bing.jsonl', 'a', encoding='utf-8')
for q in sys.argv[1:]:
    r = requests.get(f'https://www.bing.com/news/search?q={quote_plus(q)}&format=rss&count=50', headers=H, timeout=40)
    print('###', q, r.status_code)
    try:
        root = ET.fromstring(r.text)
    except Exception:
        print('parse fail'); continue
    for it in root.iter('item'):
        link = it.findtext('link') or ''
        u = parse_qs(urlparse(link).query).get('url', [link])[0]
        d = dict(q=q, title=it.findtext('title'), date=(it.findtext('pubDate') or '')[5:16], url=u,
                 snip=re.sub('<[^>]+>', ' ', html.unescape(it.findtext('description') or ''))[:350])
        out.write(json.dumps(d) + '\n')
        print(d['date'], '|', d['title'][:110], '|', u[:140]); print('    ', d['snip'][:300])
    time.sleep(1)
