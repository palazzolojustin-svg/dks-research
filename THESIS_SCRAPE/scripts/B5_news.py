"""B5: Google News / Bing News RSS helper with retries. Usage: python B5_news.py "query1" "query2" ...
Prints date | title | link for up to 15 items per query.
"""
import sys, time, re, html, urllib.parse, requests
H = {'User-Agent': 'Mozilla/5.0 (research; palazzolojustin@gmail.com)'}

def get(u):
    for a in range(4):
        try:
            return requests.get(u, headers=H, timeout=30).text
        except Exception as e:
            time.sleep(3 + 3 * a)
    return ''

for q in sys.argv[1:]:
    eng = 'g'
    if q.startswith('bing:'):
        eng, q = 'b', q[5:]
    u = ('https://news.google.com/rss/search?q=' + urllib.parse.quote(q) + '&hl=en-US&gl=US&ceid=US:en') if eng == 'g' else \
        ('https://www.bing.com/news/search?q=' + urllib.parse.quote(q) + '&format=rss')
    t = get(u)
    items = re.findall(r'<item>.*?<title>(.*?)</title>.*?<link>(.*?)</link>.*?<pubDate>(.*?)</pubDate>', t, re.S)
    print('==', eng, q, len(items))
    for ti, l, d in items[:15]:
        print('  ', d[5:16], '|', html.unescape(ti)[:140], '|', l[:160])
    time.sleep(1.5)
