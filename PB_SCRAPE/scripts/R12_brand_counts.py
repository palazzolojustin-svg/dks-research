"""R12: per-brand listing counts (X_BRAND facet) summed over categories matched between two periods.
Owned brands vs key national brands, so owned growth is shown against named competitors.
Reads raw/R12_wb_plp.csv, raw/R12_cc_plp.csv, X02 cache and X02 live facets via R12_build_table.load().
Rerun: python PB_SCRAPE\\scripts\\R12_brand_counts.py
"""
import os, sys
from collections import Counter
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from R12_build_table import load, PERIODS
from R12_common import RAW

obs, owned, flagged = load()
tgt = {n: datetime.strptime(t, "%Y%m%d") for n, a, b, t in PERIODS}
cell = {}
for o in obs:
    if not o["period"] or not o["facet_sum"]:
        continue
    k = (o["host"], o["slug"], o["period"])
    dist = abs((datetime.strptime(o["d8"], "%Y%m%d") - tgt[o["period"]]).days)
    if k not in cell or dist < cell[k][0]:
        cell[k] = (dist, o)
NAT = ["Nike", "adidas", "Under Armour", "lululemon", "Vuori", "The North Face", "Columbia", "PUMA", "New Balance", "On",
       "Brooks", "HOKA", "Jordan", "FP Movement", "Titleist", "Callaway", "TaylorMade", "Bridgestone", "Srixon",
       "YETI", "Coleman", "Stanley", "Wilson", "Rawlings", "Schwinn", "Mongoose", "Bowflex", "TravisMathew", "Tail"]
out = []
for a, b in [("25B", "LIVE"), ("25B", "26B"), ("24A", "25B"), ("24A", "LIVE")]:
    keys = [(h, s) for (h, s, p) in cell if p == a and (h, s, b) in cell]
    ca, cb = Counter(), Counter()
    for h, s in keys:
        ca.update({k: int(v) for k, v in cell[(h, s, a)][1]["brands"].items()})
        cb.update({k: int(v) for k, v in cell[(h, s, b)][1]["brands"].items()})
    ta, tb = sum(ca.values()), sum(cb.values())
    print(f"\n{a} -> {b}: {len(keys)} matched categories; all listings {ta} -> {tb} ({100*(tb/ta-1):+.0f}%)")
    oa = sum(v for k, v in ca.items() if k in owned); ob = sum(v for k, v in cb.items() if k in owned)
    print(f"  OWNED total {oa} -> {ob} ({100*(ob/max(oa,1)-1):+.0f}%)  share {100*oa/ta:.1f}% -> {100*ob/tb:.1f}%")
    for k in sorted(owned, key=lambda k: -(ca[k] + cb[k])):
        if ca[k] or cb[k]:
            print(f"  own  {k:22s} {ca[k]:>5} -> {cb[k]:>5} ({100*(cb[k]/ca[k]-1) if ca[k] else float('nan'):+.0f}%)")
            out.append([a, b, len(keys), "owned", k, ca[k], cb[k]])
    for k in NAT:
        if ca[k] or cb[k]:
            print(f"  nat  {k:22s} {ca[k]:>5} -> {cb[k]:>5} ({100*(cb[k]/ca[k]-1) if ca[k] else float('nan'):+.0f}%)")
            out.append([a, b, len(keys), "national", k, ca[k], cb[k]])
import csv
with open(os.path.join(RAW, "R12_brand_counts.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh); w.writerow(["from", "to", "n_cats", "type", "brand", "count_from", "count_to"]); w.writerows(out)
