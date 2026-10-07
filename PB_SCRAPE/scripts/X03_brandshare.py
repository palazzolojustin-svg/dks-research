"""X03: owned-brand share of brand-facet counts per PLP capture (from raw/X03_cc_plp.csv and raw/X03_plp_facets.csv).
Usage: python X03_brandshare.py [slug-regex]
"""
import os, sys, re, csv, collections
RAW = os.path.join(os.path.dirname(__file__), "..", "raw")
OWN = re.compile(r"^(CALIA|CALIA by Carrie Underwood|VRST|DSG|Maxfli|MAXFLI|Walter Hagen|Alpine Design|ETHOS|Fitness Gear|Nishiki|Quest|Top Flite|Top-Flite|Tommy Armour|DSG Pro|Field & Stream)$", re.I)
flt = re.compile(sys.argv[1]) if len(sys.argv) > 1 else re.compile(".")
data = collections.defaultdict(dict)
meta = {}
for fn in ("X03_cc_plp.csv", "X03_plp_facets.csv"):
    p = os.path.join(RAW, fn)
    if not os.path.exists(p):
        continue
    for r in csv.DictReader(open(p, encoding="utf-8")):
        if not flt.search(r["slug"]):
            continue
        k = (r["slug"], r["ts"])
        meta[k] = r["total"]
        if r["attr"] == "X_BRAND":
            data[k][r["value"]] = int(r["count"])
for k in sorted(meta):
    b = data.get(k, {})
    if not b:
        continue
    tot = sum(b.values())
    own = {n: c for n, c in b.items() if OWN.match(n.strip())}
    print(k[0], k[1][:8], "total", meta[k], "facet_sum", tot, "n_brands", len(b), "owned", sum(own.values()), f"{sum(own.values()) / tot:.1%}" if tot else "", own)
