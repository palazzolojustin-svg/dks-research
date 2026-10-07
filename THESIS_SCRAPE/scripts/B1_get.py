"""B1: generic fetch helper. python B1_get.py URL [out_path] [--links pattern] [--text]
Prints status/content-type/size; saves body if out_path given; --links prints hrefs matching regex; --text prints visible text (first 8000 chars).
"""
import sys, re, requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0 Safari/537.36',
     'Accept-Language': 'en-US,en;q=0.9'}
url = sys.argv[1]
args = sys.argv[2:]
out = args[0] if args and not args[0].startswith('--') else None
r = requests.get(url, headers=H, timeout=90)
print(r.status_code, r.headers.get('content-type'), len(r.content), r.url)
if out:
    open(out, 'wb').write(r.content)
if '--links' in args:
    pat = args[args.index('--links') + 1]
    s = BeautifulSoup(r.text, 'html.parser')
    seen = set()
    for a in s.find_all('a', href=True):
        h = urljoin(r.url, a['href'])
        t = a.get_text(' ', strip=True)
        if re.search(pat, h + ' ' + t, re.I) and h not in seen:
            seen.add(h); print(' ', t[:100], '|', h)
if '--raw' in args:
    pat = args[args.index('--raw') + 1]
    for m in sorted(set(re.findall(r'(?:src|href|data-url)=["\']([^"\']+)["\']', r.text))):
        if re.search(pat, m, re.I): print('  RAW', m)
if '--text' in args:
    s = BeautifulSoup(r.text, 'html.parser')
    for t in s(['script', 'style']): t.decompose()
    n = int(args[args.index('--text') + 1]) if len(args) > args.index('--text') + 1 and args[args.index('--text') + 1].isdigit() else 8000
    print(re.sub(r'\s+', ' ', s.get_text(' '))[:n])
