"""D04: lightweight DuckDuckGo HTML search (used after WebSearch budget ran out).
Usage: python D04_ddg.py "query" [n]"""
import sys, requests, time
from bs4 import BeautifulSoup
from urllib.parse import unquote, urlparse, parse_qs
q = sys.argv[1]; n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
h = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36'}
r = requests.post('https://html.duckduckgo.com/html/', data={'q': q}, headers=h, timeout=30)
s = BeautifulSoup(r.text, 'html.parser')
print('STATUS', r.status_code)
for i, res in enumerate(s.select('.result')[:n]):
    a = res.select_one('.result__a'); sn = res.select_one('.result__snippet')
    if not a: continue
    href = a.get('href', '')
    if 'uddg=' in href:
        href = unquote(parse_qs(urlparse(href).query).get('uddg', [href])[0])
    print(f'[{i}] {a.get_text(" ", strip=True)}\n    {href}\n    {sn.get_text(" ", strip=True) if sn else ""}')
