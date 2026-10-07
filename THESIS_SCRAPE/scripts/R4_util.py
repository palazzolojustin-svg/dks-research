"""R4 helper: cached fetch + link listing + PDF text grep.
Usage: python R4_util.py links <url> [regex]      -> list hrefs (filtered)
       python R4_util.py get <url>                -> save to raw/R4_docs, print path + size
       python R4_util.py grep <url_or_path> <regex> -> PDF/HTML text lines matching regex (with page no.)
       python R4_util.py gnews <query>            -> Google News RSS titles/links
"""
import sys, os, re, hashlib, requests, urllib.parse
from bs4 import BeautifulSoup
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) research contact palazzolojustin@gmail.com'}
D = os.path.join(os.path.dirname(__file__), '..', 'raw', 'R4_docs')
os.makedirs(D, exist_ok=True)

def get(url, force=False):
    h = hashlib.md5(url.encode()).hexdigest()[:10]
    base = re.sub(r'[^A-Za-z0-9]+', '_', url.split('?')[0].split('/')[-1] or 'index')[-60:]
    p = os.path.join(D, f'{h}_{base}')
    if os.path.exists(p) and not force:
        return p, open(p, 'rb').read()
    r = requests.get(url, headers=UA, timeout=60, allow_redirects=True)
    print(f'[{r.status_code}] {url} -> {len(r.content)}B ct={r.headers.get("content-type")}', file=sys.stderr)
    open(p, 'wb').write(r.content)
    return p, r.content

def text_of(p, b):
    if b[:4] == b'%PDF':
        import fitz
        doc = fitz.open(p)
        return [(i + 1, pg.get_text()) for i, pg in enumerate(doc)]
    return [(0, BeautifulSoup(b, 'html.parser').get_text('\n'))]

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'links':
        p, b = get(sys.argv[2], force=True)
        rx = re.compile(sys.argv[3], re.I) if len(sys.argv) > 3 else None
        s = BeautifulSoup(b, 'html.parser')
        for a in s.find_all('a', href=True):
            t = a.get_text(' ', strip=True)
            u = urllib.parse.urljoin(sys.argv[2], a['href'])
            if not rx or rx.search(u + ' ' + t):
                print(t[:90], '|', u)
    elif cmd == 'get':
        p, b = get(sys.argv[2])
        print(p, len(b))
    elif cmd == 'grep':
        src = sys.argv[2]
        if os.path.exists(src):
            p, b = src, open(src, 'rb').read()
        else:
            p, b = get(src)
        rx = re.compile(sys.argv[3], re.I)
        ctx = int(sys.argv[4]) if len(sys.argv) > 4 else 0
        for pg, t in text_of(p, b):
            L = t.split('\n')
            for i, l in enumerate(L):
                if rx.search(l):
                    print(f'p{pg}:', ' / '.join(x.strip() for x in L[max(0, i - ctx):i + ctx + 1]))
        print('pages', len(text_of(p, b)), file=sys.stderr)
    elif cmd == 'gnews':
        q = urllib.parse.quote(sys.argv[2])
        r = requests.get(f'https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en', headers=UA, timeout=30)
        for it in BeautifulSoup(r.content, 'xml').find_all('item')[:40]:
            print(it.pubDate.text[:16], '|', it.title.text, '|', it.link.text)
