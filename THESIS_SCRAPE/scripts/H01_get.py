"""H01 generic page fetcher (WebFetch is blocked in this env). Saves cleaned text of each URL to raw/H01_web/<slug>.txt
and prints text lines matching a keyword regex.
Rerun: python H01_get.py "<regex>" url1 url2 ...
"""
import sys, os, re, time, requests
from bs4 import BeautifulSoup
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, 'raw', 'H01_web'); os.makedirs(OUT, exist_ok=True)
H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36',
     'Accept-Language': 'en-US,en;q=0.9', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
pat = re.compile(sys.argv[1], re.I)
for url in sys.argv[2:]:
    slug = re.sub(r'[^A-Za-z0-9]+', '_', url.split('//')[-1])[:120]
    try:
        r = requests.get(url, headers=H, timeout=45)
    except Exception as e:
        print('ERR', url, e); continue
    soup = BeautifulSoup(r.text, 'html.parser')
    for t in soup(['script', 'style', 'noscript']):
        t.decompose()
    meta = ' | '.join(f"{m.get('property') or m.get('name')}={m.get('content')}" for m in soup.find_all('meta')
                      if (m.get('property') or m.get('name') or '').lower() in ('article:published_time', 'og:title', 'description', 'author', 'date', 'og:description', 'parsely-pub-date'))
    text = soup.get_text('\n', strip=True)
    with open(os.path.join(OUT, slug + '.txt'), 'w', encoding='utf-8') as f:
        f.write(f'URL: {url}\nSTATUS: {r.status_code}\nMETA: {meta}\n\n{text}')
    print(f'##### {r.status_code} {url}\nMETA: {meta}')
    lines = text.split('\n')
    for i, l in enumerate(lines):
        if pat.search(l):
            print('  >', ' '.join(lines[max(0, i - 1):i + 2])[:600])
    time.sleep(1)
