"""P1 helper: fetch URL(s) (requests+bs4), save text to raw/P1_articles/<slug>.txt, print keyword windows.
Rerun: python P1_url.py "<regex>" <url1> [url2 ...]"""
import sys, os, re
sys.path.insert(0, os.path.dirname(__file__))
from H02_fetch_text import text_of
OUTD = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\P1_articles'; os.makedirs(OUTD, exist_ok=True)
pat = re.compile(sys.argv[1], re.I)
for u in sys.argv[2:]:
    try:
        code, meta, t = text_of(u)
    except Exception as e:
        print('##ERR', u, str(e)[:120]); continue
    slug = re.sub(r'[^A-Za-z0-9]+', '_', u.split('//')[-1])[:80]
    open(os.path.join(OUTD, slug + '.txt'), 'w', encoding='utf-8').write(f'URL: {u}\nCODE: {code}\nMETA: {meta}\n\n{t}')
    print('##', code, len(t), u, meta[:2])
    last = -999
    n = 0
    for m in pat.finditer(t):
        if m.start() - last < 500:
            continue
        last = m.start(); n += 1
        print('   ..', t[max(0, m.start() - 300): m.end() + 400])
        if n >= 12:
            break
