"""X03: owned-brand share of product assortment in dicks.com category pages, base season vs compare season.
Uses raw/X03_cc_plp.csv + raw/X03_plp_facets.csv. Only captures where the brand facet is fully rendered
(sum of brand facet counts >= 95% of totalCount) are used, so owned counts and totals are complete.
For each slug picks the capture closest to the target month in each window.
Output: raw/X03_apparel_panel.csv
Usage: python X03_apparel_panel.py [base_from base_to cmp_from cmp_to]   (YYYYMM, default 202507 202510 202605 202609)
"""
import os, sys, csv, re, collections
RAW = os.path.join(os.path.dirname(__file__), "..", "raw")
OWN = re.compile(r"^(CALIA|CALIA by Carrie Underwood|VRST|DSG|Maxfli|Walter Hagen|Alpine Design|ETHOS|Fitness Gear|Nishiki|Quest|Top Flite|Tommy Armour)$", re.I)
a = sys.argv[1:] or ["202507", "202510", "202605", "202609"]
bf, bt, cf, ct = a
caps = collections.defaultdict(lambda: {"total": None, "brands": {}})
for fn in ("X03_cc_plp.csv", "X03_plp_facets.csv"):
    p = os.path.join(RAW, fn)
    if os.path.exists(p):
        for r in csv.DictReader(open(p, encoding="utf-8")):
            k = (r["slug"], r["ts"])
            if r["attr"] == "_TOTAL":
                caps[k]["total"] = int(r["count"]) if r["count"] not in ("", "None") else None
            elif r["attr"] == "X_BRAND":
                caps[k]["brands"][r["value"]] = int(r["count"])
full = {k: v for k, v in caps.items() if v["total"] and v["brands"] and sum(v["brands"].values()) >= 0.95 * v["total"]}
byslug = collections.defaultdict(list)
for (s, ts), v in full.items():
    byslug[s].append((ts, v))
out = []
for s, lst in sorted(byslug.items()):
    if re.match(r"^f/(calia|vrst|dsg|maxfli|walter|alpine|ethos|fitness-gear|nishiki|quest|top-flite|tommy)", s) or re.search(r"sale|clearance|gift|new-arrivals", s):
        continue
    base = [x for x in lst if bf <= x[0][:6] <= bt]
    cmp_ = [x for x in lst if cf <= x[0][:6] <= ct]
    if not base or not cmp_:
        continue
    b, c = base[-1], cmp_[-1]
    ob = sum(n for k, n in b[1]["brands"].items() if OWN.match(k.strip()))
    oc = sum(n for k, n in c[1]["brands"].items() if OWN.match(k.strip()))
    out.append({"slug": s, "ts_base": b[0], "total_base": b[1]["total"], "owned_base": ob, "share_base": round(ob / b[1]["total"], 4),
                "ts_cmp": c[0], "total_cmp": c[1]["total"], "owned_cmp": oc, "share_cmp": round(oc / c[1]["total"], 4)})
for r in out:
    print(f"{r['slug']:<32} {r['ts_base'][:8]} {r['owned_base']:>4}/{r['total_base']:<5} {r['share_base']:.1%} -> {r['ts_cmp'][:8]} {r['owned_cmp']:>4}/{r['total_cmp']:<5} {r['share_cmp']:.1%}")
if out:
    ob = sum(r["owned_base"] for r in out); tb = sum(r["total_base"] for r in out)
    oc = sum(r["owned_cmp"] for r in out); tc = sum(r["total_cmp"] for r in out)
    up = sum(1 for r in out if r["share_cmp"] > r["share_base"])
    print(f"POOLED N={len(out)}: owned {ob}->{oc} ({oc / ob - 1:+.1%}), total {tb}->{tc} ({tc / tb - 1:+.1%}), share {ob / tb:.2%} -> {oc / tc:.2%}; share up in {up}/{len(out)}")
    with open(os.path.join(RAW, f"X03_apparel_panel_{bf}_{cf}.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
