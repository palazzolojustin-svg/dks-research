"""B4: fetch decoded FH/next-gen articles and extract keyword windows (size, jobs, sales, relocation).
Rerun: python B4_fetch_articles.py  -> raw/B4_article_snips.txt
"""
import json, re, time
from H02_fetch_text import text_of
R = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\\'
d = json.load(open(R + 'B4_decoded.json'))
extra = ['https://www.dailyfreeman.com/2026/03/04/dicks-sporting-goods-leaves-mall-set-to-open-at-hudson-valley-plaza-on-march-20/',
         'https://www.vindy.com/news/business-news/2026/06/dicks-sporting-goods-to-unveil-new-location/']
urls = [u for u in d.values() if u] + extra
skip = ('houseofheat', 'retailtouchpoints', 'kktv', 'panda', 'meijer', 'gas-station', 'two-new-businesses', 'petco')
kw = re.compile(r'(square[- ]f|sq\.? ?ft|feet|employ|jobs|hire|million|\$\d|larger|bigger|relocat|field house|next[- ]gen|former|closing|close[sd]?\b|percent|%)', re.I)
out = []
for u in urls:
    if any(s in u for s in skip):
        continue
    try:
        code, meta, t = text_of(u)
    except Exception as e:
        out.append(f'### {u}\nERR {e}\n'); continue
    i = max(t.find('Dick'), 0)
    body = t
    snips = []
    for m in kw.finditer(body):
        s = body[max(0, m.start() - 220): m.end() + 220]
        if 'ick' in s and (not snips or m.start() - snips[-1][0] > 300):
            snips.append((m.start(), s))
    out.append(f'### {u} [{code}] {meta}\n' + '\n'.join('- ' + s for _, s in snips[:14]))
    print(u, code, len(snips), flush=True)
    time.sleep(1)
open(R + 'B4_article_snips.txt', 'w', encoding='utf8').write('\n\n'.join(out))
