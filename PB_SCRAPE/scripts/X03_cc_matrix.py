"""X03: which dicks.com /f/ slugs appear (HTTP 200, no query) in which Common Crawl collections.
Usage: python X03_cc_matrix.py [regex-filter] [min_collections=4]
"""
import sys, os, re, json, glob, collections

RAW = os.path.join(os.path.dirname(__file__), "..", "raw", "X03_cc")
flt = re.compile(sys.argv[1]) if len(sys.argv) > 1 else None
mn = int(sys.argv[2]) if len(sys.argv) > 2 else 4
pres = collections.defaultdict(set)
colls = []
for fn in sorted(glob.glob(os.path.join(RAW, "*_f.jsonl"))):
    c = os.path.basename(fn).split("_")[0]
    colls.append(c)
    for l in open(fn, encoding="utf-8"):
        try:
            r = json.loads(l)
        except Exception:
            continue
        if r.get("status") != "200" or "?" in r["url"]:
            continue
        slug = re.sub(r"^https?://[^/]+/", "", r["url"]).rstrip("/").lower()
        pres[slug].add(c)
print("collections:", colls)
rows = sorted(((len(v), k) for k, v in pres.items() if (flt is None or flt.search(k)) and len(v) >= mn), reverse=True)
for n, k in rows[:300]:
    print(n, k, "".join("X" if c in pres[k] else "." for c in colls))
