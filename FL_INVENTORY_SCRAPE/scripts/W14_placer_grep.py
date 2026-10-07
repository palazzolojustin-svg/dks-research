"""W14: fetch Placer.ai Anchor articles (sitemap lastmod >= cutoff) and grep for FL banners.
Usage: python3 -I W14_placer_grep.py 2025-06-01
Outputs raw/W14/placer_hits.jsonl (url, lastmod, published, snippets)."""
import re, sys, json, time, os, requests
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup as B
RAW = '/home/user/dks-research/FL_INVENTORY_SCRAPE/raw/W14'
H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36'}
cut = sys.argv[1] if len(sys.argv) > 1 else '2025-06-01'
sm = open(f'{RAW}/placer_sitemap.xml').read()
items = re.findall(r'<loc>([^<]*anchor/articles[^<]*)</loc>\s*<lastmod>([^<]*)</lastmod>', sm)
items = [(u, l) for u, l in items if l[:10] >= cut]
print(len(items), 'articles since', cut, flush=True)
done = set()
OUT = f'{RAW}/placer_hits.jsonl'
if os.path.exists(OUT):
    for line in open(OUT):
        done.add(json.loads(line)['url'])
KW = re.compile(r'foot ?locker|champs|kids foot|sneaker|fast break|athletic footwear|footwear', re.I)
def work(it):
    u, l = it
    if u in done: return None
    for i in range(3):
        try:
            r = requests.get(u, headers=H, timeout=60)
            if r.status_code == 200: break
            time.sleep(5)
        except Exception:
            time.sleep(5)
    else:
        return {'url': u, 'lastmod': l, 'err': True}
    t = r.text
    m = re.search(r'"datePublished"\s*:\s*"([^"]+)"', t)
    pub = m.group(1) if m else ''
    txt = B(t, 'html.parser').get_text(' ', strip=True)
    hits = []
    for mm in re.finditer(r'foot ?locker|champs sports|fast break', txt, re.I):
        hits.append(txt[max(0, mm.start()-400):mm.end()+600])
    return {'url': u, 'lastmod': l, 'pub': pub, 'n_fl': len(hits), 'snips': hits[:8], 'fw': len(KW.findall(txt))}
with ThreadPoolExecutor(6) as ex, open(OUT, 'a') as f:
    for res in ex.map(work, items):
        if res:
            f.write(json.dumps(res) + '\n'); f.flush()
            if res.get('n_fl'): print(res['url'], res['pub'], res['n_fl'], flush=True)
