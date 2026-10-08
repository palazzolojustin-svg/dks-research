"""V2: composition checks. (1) re-weight 2026 on-sale/avg-disc to the 2025 mix of primary category (attr PRIMARY_CATEGORY_DSG) for Aug+Sep;
(2) national, matched pages median of page-level diffs; (3) Nike/adidas excl. footwear? (category mix only)."""
import json, os, collections, statistics as st, sys
sys.argv = ["x"]; sys.path.insert(0, os.path.dirname(__file__))
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "V2_analyze.py")).read().replace("\nmain()\n", "\n")
g = {"__file__": os.path.join(os.path.dirname(os.path.abspath(__file__)), "V2_analyze.py")}; exec(compile(src, "a", "exec"), g)
load, M, owned, sale, depth = g["load"], g["M"], g["owned"], g["sale"], g["depth"]
A = [r for c in ("CC-MAIN-2025-33", "CC-MAIN-2025-38") for r in load(c) if not owned(r)]
B = [r for c in ("CC-MAIN-2026-34", "CC-MAIN-2026-39") for r in load(c) if not owned(r)]
def bycat(rs):
    d = collections.defaultdict(list)
    for r in rs:
        if g["valid"](r): d[r["cat"] or "NA"].append(r)
    return d
ca, cb = bycat(A), bycat(B); na = sum(len(v) for v in ca.values())
for key, fn in [("on_sale", lambda rs: M(rs)["on_sale"]), ("avg_disc", lambda rs: M(rs)["avg_disc"])]:
    w = tot = 0
    for c, v in ca.items():
        if len(v) >= 20 and len(cb.get(c, [])) >= 20: w += len(v); tot += len(v) * fn(cb[c])
    w2 = sum(len(v) for c, v in ca.items() if len(v) >= 20 and len(cb.get(c, [])) >= 20)
    base = sum(len(v) * fn(v) for c, v in ca.items() if len(v) >= 20 and len(cb.get(c, [])) >= 20) / w2
    print("national", key, "2025 on matched cats", round(100 * base, 1), "-> 2026 at 2025 category mix", round(100 * tot / w2, 1), "cats", sum(1 for c, v in ca.items() if len(v) >= 20 and len(cb.get(c, [])) >= 20), "share of 2025 products covered", round(w2 / na, 2))
# top categories
for c, v in sorted(ca.items(), key=lambda x: -len(x[1]))[:8]:
    if len(cb.get(c, [])) >= 20: print(c[:28], len(v), len(cb[c]), round(100 * M(v)["on_sale"], 1), "->", round(100 * M(cb[c])["on_sale"], 1), "depth", round(100 * M(v)["depth_on_sale"], 1), "->", round(100 * M(cb[c])["depth_on_sale"], 1))
# like-for-like products present in both periods
pa = {r["pp"]: r for r in A}; pb = {r["pp"]: r for r in B}; com = [p for p in pa if p in pb]
print("same product in both periods", len(com), "on-sale", round(100 * sum(1 for p in com if sale(pa[p])) / len(com), 1), "->", round(100 * sum(1 for p in com if sale(pb[p])) / len(com), 1))
# price level: mean list and offer of on-shelf national, and median offer
import statistics
print("median national offer $", statistics.median(float(r["offer"]) for r in A if g["valid"](r)), "->", statistics.median(float(r["offer"]) for r in B if g["valid"](r)), "mean offer", round(statistics.mean(float(r["offer"]) for r in A if g["valid"](r)), 2), "->", round(statistics.mean(float(r["offer"]) for r in B if g["valid"](r)), 2), "mean list", round(statistics.mean(float(r["list"]) for r in A if g["valid"](r)), 2), "->", round(statistics.mean(float(r["list"]) for r in B if g["valid"](r)), 2))
