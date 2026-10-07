"""X03: dicks.com PLP history from Common Crawl WARCs (no Wayback rate limits).

Reads raw/X03_cc/<collection>_f.jsonl (built by X03_cc_census.py), and for every HTTP-200 capture of the
requested slugs fetches the WARC record (range request to data.commoncrawl.org), caches the HTML in
raw/X03_cc_cache/, and extracts: totalCount, brand facet (X_BRAND) counts, Sale facet, and the brand of
the first products rendered on the page (default sort = merchandised order).
Output: raw/X03_cc_plp.csv (long format) and raw/X03_cc_plp_products.csv
Usage: python X03_cc_plp.py f/maxfli f/top-flite f/calia-view-all ...
       python X03_cc_plp.py @slugfile.txt
"""
import sys, os, re, json, glob, csv, hashlib
sys.path.insert(0, os.path.dirname(__file__))
from X03_cc import cc_fetch
from X03_plp import parse

RAW = os.path.join(os.path.dirname(__file__), "..", "raw")
CACHE = os.path.join(RAW, "X03_cc_cache")
os.makedirs(CACHE, exist_ok=True)


def product_brands(html):
    """brand of products in page order, from embedded product JSON (2022-24: attributes X_BRAND; 2025-26: try several keys)."""
    out = []
    for m in re.finditer(r'\\"X_BRAND\\":\\"([^\\"]+)\\"', html):
        out.append(m.group(1))
    if not out:
        for m in re.finditer(r'"(?:brand|X_BRAND|mfName|manufacturer)"\s*:\s*"([^"]{1,40})"', html):
            out.append(m.group(1))
    return out


def get_html(r):
    key = hashlib.md5((r["filename"] + r["offset"]).encode()).hexdigest()
    fn = os.path.join(CACHE, key + ".html")
    if os.path.exists(fn):
        return open(fn, encoding="utf-8", errors="replace").read()
    t = cc_fetch(r["filename"], r["offset"], r["length"])
    if t:
        open(fn, "w", encoding="utf-8").write(t)
    return t


def main(slugs):
    want = {s.strip("/").lower() for s in slugs}
    caps = []
    for fn in sorted(glob.glob(os.path.join(RAW, "X03_cc", "*_f.jsonl"))):
        coll = os.path.basename(fn).split("_")[0]
        for l in open(fn, encoding="utf-8"):
            try:
                r = json.loads(l)
            except Exception:
                continue
            if r.get("status") != "200" or "?" in r["url"]:
                continue
            slug = re.sub(r"^https?://[^/]+/", "", r["url"]).rstrip("/").lower()
            if slug in want:
                r["coll"], r["slug"] = coll, slug
                caps.append(r)
    out = open(os.path.join(RAW, "X03_cc_plp.csv"), "w", newline="", encoding="utf-8")
    w = csv.writer(out)
    w.writerow(["slug", "collection", "ts", "total", "attr", "value", "count"])
    pout = open(os.path.join(RAW, "X03_cc_plp_products.csv"), "w", newline="", encoding="utf-8")
    pw = csv.writer(pout)
    pw.writerow(["slug", "collection", "ts", "rank", "brand"])
    for r in sorted(caps, key=lambda x: (x["slug"], x["timestamp"])):
        html = get_html(r)
        if not html:
            print("fail", r["slug"], r["timestamp"], flush=True)
            continue
        total, fac = parse(html)
        pb = product_brands(html)
        print(r["slug"], r["timestamp"], "total", total, "brands", fac.get("X_BRAND", {}) if len(fac.get("X_BRAND", {})) < 8 else len(fac.get("X_BRAND", {})), "sale", fac.get("5004"), "prod", len(pb), flush=True)
        w.writerow([r["slug"], r["coll"], r["timestamp"], total, "_TOTAL", "", total])
        for attr, vals in fac.items():
            for v, n in vals.items():
                w.writerow([r["slug"], r["coll"], r["timestamp"], total, attr, v, n])
        for i, b in enumerate(pb[:120]):
            pw.writerow([r["slug"], r["coll"], r["timestamp"], i + 1, b])
    out.close(); pout.close()


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0].startswith("@"):
        a = [l.strip() for l in open(a[0][1:]) if l.strip() and not l.startswith("#")]
    main(a)
