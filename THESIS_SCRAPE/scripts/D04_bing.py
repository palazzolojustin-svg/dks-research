"""D04: plain Bing HTML search fallback (no bot-evasion; stops if challenged).
Usage: python D04_bing.py "query" [n]"""
import sys, requests
from bs4 import BeautifulSoup
q = sys.argv[1]; n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
h = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36', 'Accept-Language': 'en-US'}
r = requests.get('https://www.bing.com/search', params={'q': q, 'setlang': 'en-US', 'cc': 'US'}, headers=h, timeout=30)
s = BeautifulSoup(r.text, 'html.parser')
items = s.select('li.b_algo')
print('STATUS', r.status_code, len(r.text), 'results', len(items))
import base64
from urllib.parse import urlparse, parse_qs
def dec(href):
    try:
        u = parse_qs(urlparse(href).query).get('u', [''])[0]
        if u.startswith('a1'):
            b = u[2:]; b += '=' * (-len(b) % 4)
            return base64.urlsafe_b64decode(b).decode('utf8', 'ignore')
    except Exception:
        pass
    return href
for li in items[:n]:
    a = li.select_one('h2 a'); p = li.select_one('p') or li.select_one('.b_caption')
    print('-', a.get_text(' ', strip=True) if a else '', '\n   ', dec(a['href']) if a else '', '\n   ', p.get_text(' ', strip=True)[:300] if p else '')
