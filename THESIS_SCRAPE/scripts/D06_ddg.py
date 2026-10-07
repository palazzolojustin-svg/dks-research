"""D06: simple web search via DuckDuckGo's public HTML endpoint (fallback when WebSearch budget is exhausted).
Usage: python THESIS_SCRAPE/scripts/D06_ddg.py "query" [max]
Prints title | url | snippet. If DDG returns a challenge page, prints BLOCKED (do not bypass).
"""
import sys, requests
from bs4 import BeautifulSoup
q = sys.argv[1]; n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36'}
r = requests.post('https://html.duckduckgo.com/html/', data={'q': q}, headers=H, timeout=40)
s = BeautifulSoup(r.text, 'html.parser')
res = s.select('.result')
if not res:
    print('BLOCKED or no results', r.status_code, len(r.text)); sys.exit()
for d in res[:n]:
    a = d.select_one('.result__a'); sn = d.select_one('.result__snippet')
    print((a.get_text(strip=True) if a else ''), '|', (a['href'] if a else ''), '|', (sn.get_text(' ', strip=True) if sn else ''))
