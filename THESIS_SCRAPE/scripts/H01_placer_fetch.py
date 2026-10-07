"""H01: fetch Placer.ai sitemap, find articles mentioning DICK'S / House of Sport / Academy / Scheels /
Foot Locker / Big 5 / sporting goods, and save cleaned article text (incl. image alt text + publish date).

Rerun:  python H01_placer_fetch.py [--sitemap] [url1 url2 ...]
  --sitemap : (re)build list of candidate article URLs from https://www.placer.ai/sitemap.xml into raw/H01_placer_urls.txt
  urls      : fetch those article URLs and append text into raw/H01_placer_articles/<slug>.txt
"""
import sys, os, re, json, requests
from bs4 import BeautifulSoup

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, 'raw')
OUT = os.path.join(RAW, 'H01_placer_articles')
os.makedirs(OUT, exist_ok=True)
H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'}
KEYS = re.compile(r"dick|house-of-sport|academy|scheels|foot-locker|big-5|sporting|athletic|hibbett|sportswear|back-to-school|bts|footwear", re.I)


def sitemap():
    urls = []
    r = requests.get('https://www.placer.ai/sitemap.xml', headers=H, timeout=60)
    locs = re.findall(r'<loc>(.*?)</loc>', r.text)
    subs = [l for l in locs if l.endswith('.xml')]
    for s in subs:
        try:
            rr = requests.get(s, headers=H, timeout=60)
            locs += re.findall(r'<loc>(.*?)</loc>', rr.text)
        except Exception as e:
            print('fail', s, e)
    locs = sorted(set(l for l in locs if not l.endswith('.xml')))
    with open(os.path.join(RAW, 'H01_placer_sitemap_all.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(locs))
    cand = [l for l in locs if KEYS.search(l)]
    with open(os.path.join(RAW, 'H01_placer_urls.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(cand))
    print(len(locs), 'total;', len(cand), 'candidates')


def get(url, tries=6):
    import time
    for i in range(tries):
        try:
            r = requests.get(url, headers=H, timeout=60)
            time.sleep(3)
            return r
        except Exception as e:
            print('retry', i, url, str(e)[:80]); time.sleep(10 * (i + 1))
    raise RuntimeError('failed ' + url)


def fetch(url):
    slug = url.rstrip('/').split('/')[-1][:120]
    if 'free-tools' in url:
        slug = 'freetool_' + slug
    r = get(url)
    with open(os.path.join(OUT, slug + '.html'), 'w', encoding='utf-8') as f:
        f.write(r.text)
    soup = BeautifulSoup(r.text, 'html.parser')
    title = soup.title.get_text(strip=True) if soup.title else ''
    meta = {m.get('property') or m.get('name'): m.get('content') for m in soup.find_all('meta') if m.get('content')}
    date = ''
    for t in soup.find_all(string=re.compile(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2}, 20\d\d')):
        date = t.strip(); break
    parts = []
    bodies = [soup.find(class_='key-takeaway-richtext'), soup.find(class_='post-body')]
    bodies = [b for b in bodies if b] or [soup.body]
    for body in bodies:
        parts.append('== ' + ' '.join(body.get('class') or []))
        txt = body.get_text(' ', strip=True)
        parts.append(re.sub(r'\s+', ' ', txt))
        for im in body.find_all('img'):
            parts.append('[IMG alt] ' + (im.get('alt') or '') + ' | ' + (im.get('src') or ''))
    txt = f'URL: {url}\nTITLE: {title}\nDATE: {date}\nDESC: {meta.get("description","")}\n\n' + '\n'.join(parts)
    with open(os.path.join(OUT, slug + '.txt'), 'w', encoding='utf-8') as f:
        f.write(txt)
    print('ok', r.status_code, slug, date, len(txt))


if __name__ == '__main__':
    args = sys.argv[1:]
    if '--sitemap' in args:
        sitemap(); args.remove('--sitemap')
    for u in args:
        try:
            fetch(u)
        except Exception as e:
            print('ERR', u, e)
