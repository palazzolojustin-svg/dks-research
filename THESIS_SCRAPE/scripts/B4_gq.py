"""B4 helper: Google News RSS quick look-up. Usage: python B4_gq.py <queries.txt> [n]"""
import sys, re, html, requests
from urllib.parse import quote
H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/127.0 Safari/537.36'}
n = int(sys.argv[2]) if len(sys.argv) > 2 else 12
for q in [l.strip().lstrip('\ufeff') for l in open(sys.argv[1], encoding='utf8') if l.strip()]:
    r = requests.get('https://news.google.com/rss/search?q=' + quote(q) + '&hl=en-US&gl=US&ceid=US:en', headers=H, timeout=30)
    its = re.findall(r'<item><title>(.*?)</title><link>(.*?)</link>.*?<pubDate>(.*?)</pubDate>', r.text)
    print('##', q, r.status_code, len(its))
    for t, l, d in its[:n]:
        print('  ', d[5:16], '|', html.unescape(t)[:130])
