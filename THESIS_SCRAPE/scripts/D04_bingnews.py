"""D04: Bing News HTML fallback. Usage: python D04_bingnews.py "query" [n]"""
import sys, requests
from bs4 import BeautifulSoup
q = sys.argv[1]; n = int(sys.argv[2]) if len(sys.argv) > 2 else 15
h = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36', 'Accept-Language': 'en-US'}
r = requests.get('https://www.bing.com/news/search', params={'q': q, 'setlang': 'en-US', 'cc': 'US', 'qft': 'sortbydate="1"'}, headers=h, timeout=30)
s = BeautifulSoup(r.text, 'html.parser')
cards = s.select('div.news-card') or s.select('.newsitem')
print('STATUS', r.status_code, 'cards', len(cards))
for c in cards[:n]:
    a = c.select_one('a.title') or c.select_one('a')
    sn = c.select_one('.snippet')
    src = c.get('data-author') or ''
    print('-', (a.get_text(' ', strip=True) if a else ''), '|', src, '\n   ', c.get('url') or (a.get('href') if a else ''), '\n   ', sn.get_text(' ', strip=True)[:300] if sn else '')
