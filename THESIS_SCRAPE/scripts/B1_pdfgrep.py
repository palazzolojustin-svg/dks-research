"""B1: download a PDF (agenda packet, staff report, traffic study) and grep its text per page.
Rerun: python B1_pdfgrep.py URL out_name "regex" [ctx_chars]
Saves raw/B1_docs/<out_name>.pdf and <out_name>.txt (pymupdf text per page); prints pages matching regex with context.
"""
import sys, re, os, requests, pymupdf
H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0 Safari/537.36'}
D = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\B1_docs'
os.makedirs(D, exist_ok=True)
url, name, pat = sys.argv[1], sys.argv[2], sys.argv[3]
ctx = int(sys.argv[4]) if len(sys.argv) > 4 else 300
p = os.path.join(D, name + '.pdf')
if not os.path.exists(p) or os.path.getsize(p) < 1000:
    with requests.get(url, headers=H, timeout=300, stream=True) as r:
        print(r.status_code, r.headers.get('content-type'), r.headers.get('content-length'))
        with open(p, 'wb') as f:
            for ch in r.iter_content(1 << 20):
                f.write(ch)
doc = pymupdf.open(p)
print('pages', len(doc), 'size', os.path.getsize(p))
txt = []
for i, pg in enumerate(doc, 1):
    t = pg.get_text()
    txt.append(f'--- p{i}\n{t}')
open(os.path.join(D, name + '.txt'), 'w', encoding='utf-8').write('\n'.join(txt))
rx = re.compile(pat, re.I)
empty = sum(1 for t in txt if len(t) < 40)
print('pages with no text layer:', empty)
for t in txt:
    head = t.split('\n', 1)[0]
    flat = re.sub(r'\s+', ' ', t)
    ms = list(rx.finditer(flat))
    if ms:
        print(f'{head}: {len(ms)} hits')
        last = -10**9
        for m in ms[:6]:
            if m.start() - last < ctx: continue
            last = m.start()
            print('   ..', flat[max(0, m.start() - ctx): m.start() + ctx])
