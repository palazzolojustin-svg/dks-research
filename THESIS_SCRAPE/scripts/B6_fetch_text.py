"""B6: fetch URLs (with retries), save visible text to raw/B6_txt_<slug>.txt, and print sentences matching a regex.
Rerun: python B6_fetch_text.py "<regex>" url1 url2 ...
PDFs are parsed with pdfplumber if installed.
"""
import requests, re, sys, os, time, io
from bs4 import BeautifulSoup
H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0 Safari/537.36'}
RAW = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw'

def get(u):
    for i in range(4):
        try:
            r = requests.get(u, headers=H, timeout=45)
            return r
        except Exception as e:
            time.sleep(3)
    return None

def text_of(r):
    ct = r.headers.get('content-type', '')
    if 'pdf' in ct or r.content[:4] == b'%PDF':
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(r.content)) as p:
                return '\n'.join((pg.extract_text() or '') for pg in p.pages)
        except Exception as e:
            return 'PDFERR ' + str(e)
    s = BeautifulSoup(r.text, 'html.parser')
    for t in s(['script', 'style', 'noscript']): t.decompose()
    return re.sub(r'[ \t]+', ' ', s.get_text('\n'))

if __name__ == '__main__':
    pat = re.compile(sys.argv[1], re.I)
    for u in sys.argv[2:]:
        r = get(u)
        if r is None: print('FAIL', u); continue
        t = text_of(r)
        slug = re.sub(r'[^A-Za-z0-9]+', '_', u.split('//')[-1])[:90]
        open(os.path.join(RAW, f'B6_txt_{slug}.txt'), 'w', encoding='utf-8').write(u + '\n' + t)
        print('=====', u, r.status_code, len(t))
        sents = re.split(r'(?<=[.!?])\s+|\n+', t)
        seen = set()
        for s in sents:
            s = s.strip()
            if s and pat.search(s) and s not in seen:
                seen.add(s); print('  -', s[:400])
