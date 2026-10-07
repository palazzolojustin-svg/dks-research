"""H06: Google News RSS search for DKS store-hiring headlines (public RSS endpoint, no login).
Rerun: python H06_gnews_hiring.py -> raw/H06_gnews_hiring.json
"""
import requests, re, json, os, time, html
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'raw')
QS = ['"House of Sport" hiring', '"House of Sport" jobs', '"House of Sport" "job fair"', '"House of Sport" employees', '"Field House" Dick\'s hiring',
      'Dick\'s Sporting Goods new store hiring', '"Dick\'s Sporting Goods" "hiring event"', '"Built to Win" Dick\'s Sporting Goods', 'Dick\'s Sporting Goods "team captain"',
      'Dick\'s Sporting Goods store managers layoffs', 'Dick\'s Sporting Goods store labor model', '"House of Sport" "employ"']
out = {}
for q in QS:
    r = None
    for a in range(4):
        try:
            r = requests.get('https://news.google.com/rss/search', params={'q': q, 'hl': 'en-US', 'gl': 'US', 'ceid': 'US:en'}, headers={'User-Agent': 'Mozilla/5.0'}, timeout=30)
            break
        except Exception as e:
            time.sleep(10 * (a + 1))
    if r is None:
        print('blocked', q); continue
    items = re.findall(r'<item>(.*?)</item>', r.text, re.S)
    rows = []
    for it in items:
        t = html.unescape(re.search(r'<title>(.*?)</title>', it, re.S).group(1))
        d = re.search(r'<pubDate>(.*?)</pubDate>', it).group(1)
        l = re.search(r'<link>(.*?)</link>', it).group(1)
        rows.append({'title': t, 'date': d, 'link': l})
    out[q] = rows
    print(q, len(rows))
    time.sleep(2)
json.dump(out, open(os.path.join(RAW, 'H06_gnews_hiring.json'), 'w'), indent=1)
