"""H01: recover Placer.ai articles that now redirect/404 via alternative paths and the Wayback Machine.
Saves cleaned text to raw/H01_placer_articles/wb_<slug>.txt
Rerun: python H01_wayback_articles.py slug1 slug2 ...
"""
import requests, re, time, os, sys
from bs4 import BeautifulSoup
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, 'raw', 'H01_placer_articles')
H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'}


def get(url, params=None, tries=5):
    for i in range(tries):
        try:
            return requests.get(url, params=params, headers=H, timeout=90)
        except Exception:
            time.sleep(8 * (i + 1))
    return None


def clean(html):
    s = BeautifulSoup(html, 'html.parser')
    for t in s(['script', 'style', 'nav', 'footer']):
        t.decompose()
    best = None
    for c in ['post-body', 'key-takeaway-richtext', 'blog-content', 'article', 'w-richtext']:
        els = s.find_all(class_=re.compile(c)) or s.find_all(c)
        for e in els:
            if best is None or len(e.get_text()) > len(best.get_text()):
                best = e
    body = best or s.body
    kt = s.find(class_='key-takeaway-richtext')
    txt = (kt.get_text(' ', strip=True) + '\n\n' if kt else '') + body.get_text(' ', strip=True)
    alts = [im.get('alt') for im in body.find_all('img') if im.get('alt')]
    title = s.title.get_text(strip=True) if s.title else ''
    return title, txt, alts


for slug in sys.argv[1:]:
    cands = [f'https://www.placer.ai/blog/{slug}', f'https://anchor.placer.ai/the-anchor/{slug}',
             f'https://www.placer.ai/anchor/articles/{slug}']
    done = False
    for u in cands[:2]:
        r = get(u)
        if r is not None and r.status_code == 200 and 'The Anchor: Location Intelligence' not in r.text[:3000]:
            t, txt, alts = clean(r.text)
            if len(txt) > 800:
                open(os.path.join(OUT, 'wb_' + slug + '.txt'), 'w', encoding='utf-8').write(f'URL: {r.url}\nTITLE: {t}\n\n{txt}\n\nIMGS: ' + ' || '.join(alts))
                print('LIVE', slug, r.url, len(txt)); done = True; break
    if done:
        continue
    for u in cands:
        cdx = get('https://web.archive.org/cdx/search/cdx', {'url': u.split('//')[1], 'output': 'json', 'filter': 'statuscode:200', 'limit': '-3'})
        if cdx is None or cdx.status_code != 200 or len(cdx.text) < 10:
            continue
        rows = cdx.json()[1:]
        if not rows:
            continue
        ts, orig = rows[0][1], rows[0][2]
        r = get(f'https://web.archive.org/web/{ts}id_/{orig}')
        if r is None:
            continue
        t, txt, alts = clean(r.text)
        open(os.path.join(OUT, 'wb_' + slug + '.txt'), 'w', encoding='utf-8').write(f'URL: {orig} (wayback {ts})\nTITLE: {t}\n\n{txt}\n\nIMGS: ' + ' || '.join(alts))
        print('WB', slug, ts, len(txt)); done = True; break
    if not done:
        print('NONE', slug)
    time.sleep(2)
