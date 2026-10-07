"""W10: quarterly Foot Locker Retail sea imports by category (apparel / packaging+fixtures / footwear) from the ImportYeti vendor table.
Usage: python3 -I W10_categories.py <payload.txt> <out.csv>"""
import sys, re, json, csv
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from W10_parse import vendors
from collections import defaultdict
PACK = ("finieco", "missing in source", "hanger", "textile decoration", "technolink")
FOOT = ("rollsport", "adonia", "galaxy active", "thai binh", "new shoes", "footwear")
def cat(v):
    n = (v.get("vendor_name") or "").lower(); d = (v.get("product_descriptions") or "").lower()
    if any(p in n for p in PACK) or "paper bag" in d: return "packaging_fixtures"
    if any(p in n for p in FOOT) or ("footwear" in d and "garment" not in d): return "footwear"
    return "apparel"
big = open(sys.argv[1], encoding="utf-8").read()
agg = defaultdict(lambda: [0, 0])
for v in vendors(big):
    c = cat(v)
    for k, x in (v.get("vendor_time_series") or {}).items():
        d, m, y = k.split('/'); q = f"{y}Q{(int(m)-1)//3+1}"
        agg[(q, c)][0] += x["shipments"]; agg[(q, c)][1] += x["weight"]
qs = sorted({q for q, _ in agg})
cats = ["apparel", "packaging_fixtures", "footwear"]
rows = []
print("quarter " + " ".join(f"{c[:10]:>18}" for c in cats))
for q in qs:
    if q < "2021": continue
    r = [q]
    for c in cats: r += agg[(q, c)]
    rows.append(r)
    print(q, " ".join(f"{agg[(q,c)][0]:>5} sh {agg[(q,c)][1]/1000:>8.1f}t" for c in cats))
with open(sys.argv[2], "w", newline="") as f:
    w = csv.writer(f); w.writerow(["quarter"] + [f"{c}_{m}" for c in cats for m in ("shipments", "kg")]); w.writerows(rows)
