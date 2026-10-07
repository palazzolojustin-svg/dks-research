"""P2_plan.py: from raw\\P2_cdx_captures.csv build a fetch plan for the Wayback price panel.
Fiscal quarters (DKS): Q3FY25 = Aug-Oct 2025, Q4FY25 = Nov 2025-Jan 2026, Q1FY26 = Feb-Apr 2026, Q2FY26 = May-Jul 2026.
Output: raw\\P2_plan_panel.csv (one capture per product per quarter for products seen in >=3 of the 4 quarters, sampled) and
        raw\\P2_plan_xsec.csv (random cross-section of products per month for promo depth).
Rerun: python P2_plan.py [n_panel] [n_per_month]
"""
import csv, re, random, sys
from collections import defaultdict
random.seed(7)
RAW = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw'
N_PANEL = int(sys.argv[1]) if len(sys.argv) > 1 else 320
N_MONTH = int(sys.argv[2]) if len(sys.argv) > 2 else 45

def fq(ts):
    y, m = int(ts[:4]), int(ts[4:6])
    if (y == 2025 and m in (8, 9, 10)): return 'Q3FY25'
    if (y == 2025 and m in (11, 12)) or (y == 2026 and m == 1): return 'Q4FY25'
    if y == 2026 and m in (2, 3, 4): return 'Q1FY26'
    if y == 2026 and m in (5, 6, 7): return 'Q2FY26'
    return None

def category(slug):
    s = slug
    if re.search(r'shoe|sneaker|cleat|boot|sandal|slide|clog|spikes|slipper', s): return 'footwear'
    if re.search(r'shirt|tee|hoodie|jacket|pant|short|legging|bra|tight|fleece|vest|jersey|sock|hat|cap|beanie|glove|polo|pullover|quarter-zip|1-4-zip|crew|jogger|top|tank|dress|skirt|coat|parka|sweat|bib|base-layer|underwear|brief|romper|swim|suit', s): return 'apparel'
    return 'hardlines'

rows = list(csv.DictReader(open(RAW + r'\P2_cdx_captures.csv', encoding='utf-8')))
caps = defaultdict(lambda: defaultdict(list))  # product -> quarter -> [(ts, original)]
seen = set()
for r in rows:
    if int(r['length'] or 0) < 20000: continue
    m = re.match(r'com,dickssportinggoods\)/p/([^/?]+)/([^/?]+)', r['urlkey'])
    if not m: continue
    q = fq(r['timestamp'])
    if not q: continue
    key = (m.group(2), r['timestamp'])
    if key in seen: continue
    seen.add(key)
    caps[m.group(2)][q].append((r['timestamp'], r['original'], m.group(1)))

qs = ['Q3FY25', 'Q4FY25', 'Q1FY26', 'Q2FY26']
multi = [p for p in caps if sum(1 for q in qs if caps[p][q]) >= 3]
both = [p for p in caps if caps[p]['Q3FY25'] and caps[p]['Q2FY26']]
print('products', len(caps), '>=3 qtrs', len(multi), 'Q3FY25&Q2FY26', len(both))
from collections import Counter
print('cat of multi', Counter(category(caps[p][qs[0]][0][2] if caps[p][qs[0]] else next(caps[p][q] for q in qs if caps[p][q])[0][2]) for p in multi))

def pick(lst):
    # prefer clean URL without query params, middle of list
    clean = [x for x in lst if '?' not in x[1]] or lst
    return clean[len(clean) // 2]

panel = random.sample(sorted(both), min(N_PANEL, len(both)))
with open(RAW + r'\P2_plan_panel.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['product', 'slug', 'category', 'quarter', 'timestamp', 'original'])
    for p in panel:
        for q in qs:
            if caps[p][q]:
                ts, orig, slug = pick(caps[p][q])
                w.writerow([p, slug, category(slug), q, ts, orig])

# cross-section by month
bymonth = defaultdict(list)
for p in caps:
    for q in qs:
        for ts, orig, slug in caps[p][q]:
            bymonth[ts[:6]].append((p, ts, orig, slug))
with open(RAW + r'\P2_plan_xsec.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['month', 'product', 'slug', 'category', 'timestamp', 'original'])
    for mth in sorted(bymonth):
        uniq = {}
        for p, ts, orig, slug in bymonth[mth]:
            uniq.setdefault(p, (ts, orig, slug))
        ps = random.sample(sorted(uniq), min(N_MONTH, len(uniq)))
        for p in ps:
            ts, orig, slug = uniq[p]
            w.writerow([mth, p, slug, category(slug), ts, orig])
        print(mth, len(uniq), len(ps))

