"""D04 generic page fetcher: python D04_fetch.py <url> [keyword1,keyword2,...] [window]
Prints status and text windows around keywords (or first 4000 chars). Saves text to raw/D04_pages/<slug>.txt"""
import sys, re, os, requests
from bs4 import BeautifulSoup
h = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36',
     'Accept-Language': 'en-US,en;q=0.9'}
url = sys.argv[1]
kws = sys.argv[2].split(',') if len(sys.argv) > 2 and sys.argv[2] else []
win = int(sys.argv[3]) if len(sys.argv) > 3 else 600
r = requests.get(url, headers=h, timeout=45)
print('STATUS', r.status_code, len(r.text))
ct = r.headers.get('content-type', '')
if 'pdf' in ct or url.lower().endswith('.pdf'):
    import io, pdfplumber
    with pdfplumber.open(io.BytesIO(r.content)) as pdf:
        txt = '\n'.join((p.extract_text() or '') for p in pdf.pages)
else:
    s = BeautifulSoup(r.text, 'html.parser')
    for t in s(['script', 'style', 'noscript']):
        t.decompose()
    txt = s.get_text(' ', strip=True)
d = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\D04_pages'
os.makedirs(d, exist_ok=True)
slug = re.sub(r'[^A-Za-z0-9]+', '_', url)[-120:]
open(os.path.join(d, slug + '.txt'), 'w', encoding='utf8').write(url + '\n' + txt)
if not kws:
    print(txt[:4000])
else:
    seen = []
    for k in kws:
        for m in re.finditer(re.escape(k), txt, re.I):
            a = max(0, m.start() - win); b = m.end() + win
            if any(abs(a - s0) < win for s0 in seen):
                continue
            seen.append(a)
            print(f'--- [{k}] ...{txt[a:b]}...')
