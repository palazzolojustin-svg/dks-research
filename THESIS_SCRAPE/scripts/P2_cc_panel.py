"""P2_cc_panel.py: build and fetch Common Crawl DKS price samples.
Modes:
  pair <crawlA> <crawlB> <N>   -> products captured (200, full page) in both crawls; fetch both; raw\\P2_ccpair_<A>_<B>.csv (variant level)
  xsec <crawl> <N>             -> random N products in a crawl; raw\\P2_ccxsec_<crawl>.csv (variant level)
Rerun e.g.: python P2_cc_panel.py pair CC-MAIN-2025-38 CC-MAIN-2026-39 400
Random seed fixed (11) so samples are reproducible; WARC records cached in raw\\P2_html.
"""
import csv, sys, os, re, random, time
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from P2_cc_fetch import cc_prices
RAW = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw'
random.seed(11)

def category(slug):
    s = slug
    if re.search(r'shoe|sneaker|cleat|boot|sandal|slide|clog|spikes|slipper|mule', s): return 'footwear'
    if re.search(r'shirt|tee|hoodie|jacket|pant|short|legging|bra|tight|fleece|vest|jersey|sock|hat|cap|beanie|glove|polo|pullover|quarter-zip|1-4-zip|crew|jogger|top|tank|dress|skirt|coat|parka|sweat|bib|base-layer|underwear|brief|romper|swim|suit|skort|anorak|windbreaker|headband|visor', s): return 'apparel'
    return 'hardlines'

def load(crawl):
    d = {}
    for r in csv.DictReader(open(RAW + r'\P2_cc_%s.csv' % crawl, encoding='utf-8')):
        if r['status'] != '200' or int(r['length'] or 0) < 100000:
            continue
        m = re.search(r'/p/([^/?]+)/([^/?]+)', r['url'])
        if not m:
            continue
        pid = m.group(2).lower()
        # prefer URL without query
        if pid not in d or ('?' in d[pid]['url'] and '?' not in r['url']):
            r['slug'] = m.group(1).lower()
            d[pid] = r
    return d

def fetch_rows(items, tag):
    def job(it):
        crawl, pid, r = it
        try:
            v, meta = cc_prices(r['filename'], r['offset'], r['length'])
            return crawl, pid, r, v, meta, 'ok'
        except Exception as e:
            return crawl, pid, r, {}, {}, 'ERR %s' % e
    out = []
    t0 = time.time()
    with ThreadPoolExecutor(6) as ex:
        for i, res in enumerate(ex.map(job, items)):
            crawl, pid, r, v, meta, st = res
            vs = [x for x in v.values() if x.get('list')]
            for x in vs:
                out.append(dict(crawl=crawl, product=pid, slug=r['slug'], category=category(r['slug']), brand=r['slug'].split('-')[0],
                                timestamp=r['timestamp'], title=meta.get('title', ''), catentry=x['catentry'], partnumber=x['parentPartNumber'],
                                clearance=x['clearance'], list=x['list'], offer=x['offer'], map=x['map'], deals=x['deals'], priceIndicator=x['priceIndicator']))
            if not vs:
                out.append(dict(crawl=crawl, product=pid, slug=r['slug'], category=category(r['slug']), brand=r['slug'].split('-')[0],
                                timestamp=r['timestamp'], title=meta.get('title', st)))
            if (i + 1) % 50 == 0:
                print(tag, i + 1, len(items), round(time.time() - t0), flush=True)
    return out

def write(rows, path):
    fields = ['crawl', 'product', 'slug', 'category', 'brand', 'timestamp', 'title', 'catentry', 'partnumber', 'clearance', 'list', 'offer', 'map', 'deals', 'priceIndicator']
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
    print('wrote', path, len(rows))

mode = sys.argv[1]
if mode == 'pair':
    A, B, N = sys.argv[2], sys.argv[3], int(sys.argv[4])
    da, db = load(A), load(B)
    common = sorted(set(da) & set(db))
    print('common products', len(common), 'A', len(da), 'B', len(db))
    pick = random.sample(common, min(N, len(common)))
    items = [(A, p, da[p]) for p in pick] + [(B, p, db[p]) for p in pick]
    write(fetch_rows(items, 'pair'), RAW + r'\P2_ccpair_%s_%s.csv' % (A[-7:], B[-7:]))
elif mode == 'xsec':
    C, N = sys.argv[2], int(sys.argv[3])
    d = load(C)
    pick = random.sample(sorted(d), min(N, len(d)))
    write(fetch_rows([(C, p, d[p]) for p in pick], 'xsec'), RAW + r'\P2_ccxsec_%s.csv' % C[-7:])
