"""H01: full-text grep of Placer.ai Anchor articles (sitemap lastmod >= START) for DICK'S / House of Sport /
Field House / Academy / Scheels / sporting goods mentions. Saves matching paragraphs to raw/H01_placer_grep.jsonl
(resumable: skips URLs already in the jsonl).
Rerun: python H01_placer_grep.py [START=2025-01-01]
"""
import requests, re, time, os, sys, json
from bs4 import BeautifulSoup
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTF = os.path.join(BASE, 'raw', 'H01_placer_grep.jsonl')
H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'}
START = sys.argv[1] if len(sys.argv) > 1 else '2025-01-01'
PAT = re.compile(r"DICK.?S|House of Sport|Field House|Academy Sports|Scheels|sporting goods|Big 5|Foot Locker|Hibbett", re.I)

sm = requests.get('https://www.placer.ai/sitemap.xml', headers=H, timeout=60).text
items = re.findall(r'<loc>(https://www\.placer\.ai/anchor/(?:articles|reports)/[^<]+)</loc>\s*<lastmod>([^<]+)</lastmod>', sm)
items = [(u, d) for u, d in items if d[:10] >= START]
done = set()
if os.path.exists(OUTF):
    for l in open(OUTF, encoding='utf-8'):
        try:
            done.add(json.loads(l)['url'])
        except Exception:
            pass
print(len(items), 'articles since', START, ';', len(done), 'done')
for u, d in items:
    if u in done:
        continue
    r = None
    for i in range(4):
        try:
            r = requests.get(u, headers=H, timeout=60); break
        except Exception:
            time.sleep(10 * (i + 1))
    if r is None:
        print('FAIL', u); continue
    s = BeautifulSoup(r.text, 'html.parser')
    pub = ''
    m = re.search(r'"datePublished"\s*:\s*"([^"]+)"', r.text)
    if m:
        pub = m.group(1)
    title = s.title.get_text(strip=True) if s.title else ''
    hits = []
    for c in ['key-takeaway-richtext', 'post-body']:
        el = s.find(class_=c)
        if not el:
            continue
        for p in el.find_all(['p', 'li', 'h2', 'h3', 'img']):
            t = p.get('alt', '') if p.name == 'img' else p.get_text(' ', strip=True)
            if t and PAT.search(t):
                hits.append(t)
    rec = {'url': u, 'lastmod': d, 'pub': pub, 'title': title, 'hits': hits}
    with open(OUTF, 'a', encoding='utf-8') as f:
        f.write(json.dumps(rec) + '\n')
    if hits:
        print('HIT', d[:10], title[:80], len(hits), flush=True)
    time.sleep(2.5)
print('done')
