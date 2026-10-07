"""P2_cc_locate.py: find the Common Crawl columnar-index parquet part(s) holding com,dickssportinggoods)/p/ for a crawl, then list
all DKS product-page captures (status, WARC filename/offset/length) in that crawl.
Rerun: python P2_cc_locate.py CC-MAIN-2026-39 [CC-MAIN-2025-38 ...] -> raw\\P2_cc_<crawl>.csv
"""
import duckdb, requests, gzip, sys, csv, time
H = {'User-Agent': 'DKS price research (palazzolojustin@gmail.com)'}
BASE = 'https://data.commoncrawl.org/'
con = duckdb.connect()
con.execute("INSTALL httpfs; LOAD httpfs;")
KEY = 'com,dickssportinggoods)/p/'

def parts(crawl):
    r = requests.get(BASE + 'crawl-data/%s/cc-index-table.paths.gz' % crawl, headers=H, timeout=120)
    return [p for p in gzip.decompress(r.content).decode().splitlines() if 'subset=warc/' in p]

def minmax(path):
    q = "select min(stats_min_value), max(stats_max_value) from parquet_metadata('%s') where path_in_schema='url_surtkey'" % (BASE + path)
    return con.execute(q).fetchone()

for crawl in sys.argv[1:]:
    ps = parts(crawl)
    lo, hi = 0, len(ps) - 1
    found = []
    # binary search on min key
    while lo < hi:
        mid = (lo + hi + 1) // 2
        mn, mx = minmax(ps[mid])
        print(crawl, mid, mn[:40], mx[:40], flush=True)
        if mn <= KEY:
            lo = mid
        else:
            hi = mid - 1
    cand = [lo]
    mn, mx = minmax(ps[lo])
    if mx < 'com,dickssportinggoods)/q':
        cand.append(lo + 1)
    print('candidate parts', cand)
    rows = []
    for c in cand:
        q = ("select url, fetch_time, fetch_status, content_mime_detected, warc_filename, warc_record_offset, warc_record_length "
             "from read_parquet('%s') where url_surtkey >= 'com,dickssportinggoods)/p/' and url_surtkey < 'com,dickssportinggoods)/p0'" % (BASE + ps[c]))
        t0 = time.time()
        res = con.execute(q).fetchall()
        print('part', c, len(res), round(time.time() - t0), 's', flush=True)
        rows += res
    with open(r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\P2_cc_%s.csv' % crawl, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['url', 'fetch_time', 'status', 'mime', 'warc_filename', 'offset', 'length'])
        w.writerows(rows)
    from collections import Counter
    print(crawl, len(rows), Counter(r[2] for r in rows).most_common(5))
