"""P2_cc_zipnum.py: list all Common Crawl captures of www.dickssportinggoods.com/p/* in a crawl WITHOUT the (unreachable) index server,
by binary-searching the crawl's cluster.idx with HTTP range requests and then range-fetching the zipnum CDX blocks.
Rerun: python P2_cc_zipnum.py CC-MAIN-2026-39 CC-MAIN-2025-38 ... -> raw\\P2_cc_<crawl>.csv (url,timestamp,status,mime,filename,offset,length)
"""
import requests, gzip, zlib, sys, json, csv, time
H = {'User-Agent': 'DKS price research (palazzolojustin@gmail.com)'}
BASE = 'https://data.commoncrawl.org/'
LO_KEY = 'com,dickssportinggoods)/p/'
HI_KEY = 'com,dickssportinggoods)/p0'

def rng(url, start, end):
    for a in range(5):
        try:
            r = requests.get(url, headers=dict(H, Range='bytes=%d-%d' % (start, end)), timeout=120)
            if r.status_code in (200, 206):
                return r.content
            time.sleep(5 * (a + 1))
        except Exception as e:
            time.sleep(5 * (a + 1))
    raise RuntimeError('range fail %s' % url)

def size(url):
    r = requests.head(url, headers=H, timeout=60)
    return int(r.headers['Content-Length'])

def lines_at(url, off, n=65536):
    b = rng(url, off, off + n).decode('utf-8', 'replace')
    ls = b.split('\n')
    if off > 0:
        ls = ls[1:]
    return [l for l in ls[:-1] if l]

def run(crawl):
    idx = BASE + 'cc-index/collections/%s/indexes/cluster.idx' % crawl
    S = size(idx)
    lo, hi = 0, S
    while hi - lo > 65536:
        mid = (lo + hi) // 2
        ls = lines_at(idx, mid)
        k = ls[0].split(' ')[0] if ls else '~'
        if k < LO_KEY:
            lo = mid
        else:
            hi = mid
    # scan forward from lo collecting blocks overlapping our key range
    blocks = []
    off = lo
    prev = None
    done = False
    while not done:
        ls = lines_at(idx, off, 262144)
        for l in ls:
            parts = l.split('\t')
            key = parts[0].split(' ')[0]
            if key >= HI_KEY:
                done = True
                if prev: blocks.append(prev)
                break
            if key >= LO_KEY and prev and not blocks:
                blocks.append(prev)  # the block before the first >= key may contain matches
            if key >= LO_KEY:
                blocks.append(parts)
            prev = parts
        off += 262144 - 1000
    # dedupe
    seen = set(); bl = []
    for b in blocks:
        t = tuple(b)
        if t not in seen:
            seen.add(t); bl.append(b)
    print(crawl, 'blocks', len(bl), flush=True)
    out = []
    for b in bl:
        fname, boff, blen = b[1], int(b[2]), int(b[3])
        raw = rng(BASE + 'cc-index/collections/%s/indexes/%s' % (crawl, fname), boff, boff + blen - 1)
        txt = zlib.decompress(raw, 16 + zlib.MAX_WBITS).decode('utf-8', 'replace')
        for l in txt.splitlines():
            sk, ts, js = l.split(' ', 2)
            if LO_KEY <= sk < HI_KEY:
                j = json.loads(js)
                out.append([j.get('url'), ts, j.get('status'), j.get('mime-detected', j.get('mime')), j.get('filename'), j.get('offset'), j.get('length')])
    with open(r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\P2_cc_%s.csv' % crawl, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f); w.writerow(['url', 'timestamp', 'status', 'mime', 'filename', 'offset', 'length']); w.writerows(out)
    from collections import Counter
    print(crawl, len(out), Counter(o[2] for o in out).most_common(6), flush=True)

for c in sys.argv[1:]:
    try:
        run(c)
    except Exception as e:
        print(c, 'ERR', e, flush=True)

