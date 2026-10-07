"""X03: fetch a few dicks.com pages per Common Crawl crawl (any page carries the site header JSON with the
mega-menu CTAs), so X03_cta_series.py can build a monthly series.
Picks up to N HTTP-200 captures per calendar month inside each crawl, preferring /f/ pages, else /p/ pages.
Usage: python X03_cc_cta_fetch.py [N=3]
"""
import os, sys, json, glob, hashlib, collections
sys.path.insert(0, os.path.dirname(__file__))
from X03_cc import cc_fetch

RAW = os.path.join(os.path.dirname(__file__), "..", "raw")
CACHE = os.path.join(RAW, "X03_cc_cache")
N = int(sys.argv[1]) if len(sys.argv) > 1 else 3

bym = collections.defaultdict(lambda: {"f": [], "p": []})
for fn in sorted(glob.glob(os.path.join(RAW, "X03_cc", "*.jsonl"))):
    kind = "f" if fn.endswith("_f.jsonl") else "p"
    for l in open(fn, encoding="utf-8"):
        try:
            r = json.loads(l)
        except Exception:
            continue
        if r.get("status") == "200" and r.get("mime", "text/html") == "text/html" and int(r.get("length", 0)) > 20000:
            bym[r["timestamp"][:6]][kind].append(r)
for m in sorted(bym):
    pool = bym[m]["f"] or bym[m]["p"]
    pool = sorted(pool, key=lambda r: r["timestamp"])
    idx = sorted({0, len(pool) // 2, len(pool) - 1})[:N]
    for i in idx:
        r = pool[i]
        fn = os.path.join(CACHE, hashlib.md5((r["filename"] + r["offset"]).encode()).hexdigest() + ".html")
        if os.path.exists(fn):
            continue
        t = cc_fetch(r["filename"], r["offset"], r["length"])
        if t:
            open(fn, "w", encoding="utf-8").write(t)
        print(m, r["timestamp"], r["url"][:90], len(t or ""), flush=True)
