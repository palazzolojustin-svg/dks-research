"""B11 probe helper. Usage: python scripts/B11_probe.py <regex> <url> [url...]
Fetches each URL, prints status and links whose href or text matches regex."""
import sys, re, requests
from bs4 import BeautifulSoup
H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36'}
pat = re.compile(sys.argv[1], re.I)
for u in sys.argv[2:]:
    try:
        r = requests.get(u, headers=H, timeout=60)
        print('##', u, r.status_code, r.headers.get('content-type'), len(r.content), r.url)
        if 'html' in (r.headers.get('content-type') or ''):
            s = BeautifulSoup(r.text, 'html.parser')
            seen = set()
            for a in s.find_all('a', href=True):
                t = (a.get_text(' ', strip=True) or '')[:100]
                if pat.search(a['href']) or pat.search(t):
                    k = (a['href'], t)
                    if k not in seen:
                        seen.add(k); print('  ', t, '|', a['href'])
    except Exception as e:
        print('##', u, 'ERR', e)
