"""B1: re-fetch the Braintree MA ZBA filings for the South Shore Plaza HoS (250 Granite St) and render every page.
Rerun: python B1_fetch_braintree.py  -> raw/B1_braintree/<id>.pdf, <id>_text.txt (pdfplumber), <id>_pNN.png (150 dpi)
"""
import requests, os, re, sys, pdfplumber, pymupdf
OUT = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\B1_braintree'
H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'}
ids = [int(x) for x in sys.argv[1:]] or [16382, 16388]
os.makedirs(OUT, exist_ok=True)
for i in ids:
    u = f'https://braintreema.gov/DocumentCenter/View/{i}'
    r = requests.get(u, headers=H, timeout=120)
    cd = r.headers.get('content-disposition', '')
    print(i, r.status_code, r.headers.get('content-type'), len(r.content), cd)
    if r.status_code != 200 or b'%PDF' not in r.content[:1024]:
        continue
    p = os.path.join(OUT, f'{i}.pdf')
    open(p, 'wb').write(r.content)
    with pdfplumber.open(p) as pdf:
        txt = []
        for n, pg in enumerate(pdf.pages, 1):
            txt.append(f'--- p{n} ({pg.width:.0f}x{pg.height:.0f})\n' + (pg.extract_text() or ''))
    open(os.path.join(OUT, f'{i}_text.txt'), 'w', encoding='utf-8').write('\n'.join(txt))
    doc = pymupdf.open(p)
    md = doc.metadata
    print('  pages', len(doc), 'meta', md)
    for n, pg in enumerate(doc, 1):
        pix = pg.get_pixmap(dpi=110)
        pix.save(os.path.join(OUT, f'{i}_p{n:02d}.png'))
