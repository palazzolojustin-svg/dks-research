"""P2_basket.py: named high-volume SKU basket, Aug-Sep 2025 vs Aug-Sep 2026, from Common Crawl DKS product pages.
For each basket family (regex on URL slug), fetch every full (status 200, >=100KB) capture in CC-MAIN-2025-33/2025-38 (Y25)
and CC-MAIN-2026-34/2026-39 (Y26); product-level median list & offer (across size/color variants); then per family:
median list / offer each year, same-product matches, and successor-model comparison (e.g., Pegasus 41 -> 42).
Output: raw\\P2_basket_products.csv (one row per product-year), printed family table.
Rerun: python P2_basket.py   (WARC records cached in raw\\P2_html)
"""
import csv, re, os, sys, statistics as st
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from P2_cc_fetch import cc_prices
RAW = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw'
FAM = {
 'Nike Pegasus': r'nike-(mens|womens)-(air-zoom-)?pegasus-\d\d-running', 'Nike Vomero': r'nike-(mens|womens)-(zoomx-)?vomero', 'Nike Air Force 1': r'air-force-1',
 'Hoka Clifton': r'hoka-(mens|womens)-clifton', 'Hoka Bondi': r'hoka-(mens|womens)-bondi', 'On Cloud': r'on-(mens|womens)-cloud', 'Brooks Ghost': r'brooks-(mens|womens)-ghost',
 'adidas Samba': r'samba', 'ASICS run': r'asics-(mens|womens)-(gel-kayano|gel-nimbus|novablast|gt-2000)', 'New Balance run/lifestyle': r'new-balance-(mens|womens|kids|grade)[^/]*(1080|880|9060|530|550)',
 'YETI Rambler': r'yeti-[^/]*rambler', 'Stanley Quencher': r'stanley-[^/]*quencher', 'Stanley other': r'stanley-(?!.*quencher)', 'YETI other': r'yeti-(?!.*rambler)',
 'Titleist balls': r'titleist-[^/]*(pro-v1|avx|velocity|tour-soft|trufeel)', 'Titleist other': r'titleist-(?!.*(pro-v1|avx|velocity|tour-soft|trufeel))',
 'Drivers (Callaway/TaylorMade/Ping)': r'(callaway|taylormade|ping)-[^/]*driver', 'Rawlings/Easton bats': r'(rawlings|easton)-[^/]*bat', 'Rawlings/Easton gloves': r'(rawlings|easton)-[^/]*glove',
 'Gatorade': r'gatorade', 'Wilson balls': r'wilson-[^/]*(basketball|football)',
}
YEARS = {'Y25': ['CC-MAIN-2025-33', 'CC-MAIN-2025-38'], 'Y26': ['CC-MAIN-2026-34', 'CC-MAIN-2026-39']}

def idx(crawl):
    out = {}
    for r in csv.DictReader(open(RAW + r'\P2_cc_%s.csv' % crawl, encoding='utf-8')):
        if r['status'] != '200' or int(r['length'] or 0) < 100000: continue
        m = re.search(r'/p/([^/?]+)/([^/?]+)', r['url'])
        if not m: continue
        pid = m.group(2).lower(); r['slug'] = m.group(1).lower(); r['crawl'] = crawl
        if pid not in out or ('?' in out[pid]['url'] and '?' not in r['url']): out[pid] = r
    return out

items = []
for y, crawls in YEARS.items():
    seen = {}
    for c in crawls:
        for pid, r in idx(c).items():
            seen.setdefault(pid, r)  # first crawl (earlier) wins
    for pid, r in seen.items():
        fam = [k for k, p in FAM.items() if re.search(p, r['slug'])]
        if fam: items.append((y, fam[0], pid, r))
print('items', len(items))

def job(it):
    y, fam, pid, r = it
    try:
        v, meta = cc_prices(r['filename'], r['offset'], r['length'])
    except Exception as e:
        return None
    vs = [x for x in v.values() if x.get('list')]
    if not vs: return None
    L = [float(x['list']) for x in vs]; O = [float(x['offer']) for x in vs]
    md = sum(1 for l, o in zip(L, O) if o < l - 0.005) / len(vs)
    return dict(year=y, family=fam, product=pid, slug=r['slug'], crawl=r['crawl'], timestamp=r['timestamp'], title=meta.get('title', '')[:120],
                nvar=len(vs), list_med=st.median(L), offer_med=st.median(O), list_min=min(L), list_max=max(L), md_share=round(md, 3),
                clearance=round(sum(1 for x in vs if str(x['clearance']) == 'True') / len(vs), 3))
with ThreadPoolExecutor(6) as ex:
    rows = [r for r in ex.map(job, items) if r]
fields = list(rows[0].keys())
with open(RAW + r'\P2_basket_products.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
print('%-34s %4s %4s %8s %8s %8s %8s %6s %6s %5s' % ('family', 'n25', 'n26', 'L25med', 'L26med', 'O25med', 'O26med', 'md25', 'md26', 'same'))
for fam in FAM:
    a = [r for r in rows if r['family'] == fam and r['year'] == 'Y25']; b = [r for r in rows if r['family'] == fam and r['year'] == 'Y26']
    if not a or not b: continue
    same = set(r['product'] for r in a) & set(r['product'] for r in b)
    print('%-34s %4d %4d %8.2f %8.2f %8.2f %8.2f %6.2f %6.2f %5d' % (fam, len(a), len(b), st.median(r['list_med'] for r in a), st.median(r['list_med'] for r in b),
          st.median(r['offer_med'] for r in a), st.median(r['offer_med'] for r in b), st.mean(r['md_share'] for r in a), st.mean(r['md_share'] for r in b), len(same)))
