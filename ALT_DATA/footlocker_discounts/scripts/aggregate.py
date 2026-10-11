"""Aggregate parsed pages (data/pages/*.jsonl) into monthly discount metrics.

Unit of analysis = unique product per region-month (sku for category grids, product_id for /buy/
SEO grids); a product seen on several pages/captures in a month is averaged.
  pct_on_sale       = share of products with price < list price (>0.5% below)
  avg_disc_all      = mean (1 - price/list) across ALL products (0 for full price) - chart's 2nd line
  avg_disc_on_sale  = mean (1 - price/list) across discounted products only (depth)
Outputs (../output): monthly_metrics.csv (region x month x segment), pages_per_month.csv
"""
import csv
import glob
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from flparse import is_nike  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "data"))
OUT = os.path.normpath(os.path.join(HERE, "..", "output"))
START, END = "202409", "202610"


def main():
    pages = defaultdict(lambda: defaultdict(int))       # (region, month) -> counters
    prods = defaultdict(list)                            # (region, month, fmt, key) -> [disc]
    meta = {}
    seen_pages = set()
    live = os.path.normpath(os.path.join(HERE, "..", "live", "pages"))
    src = live if glob.glob(os.path.join(live, "*.jsonl")) else os.path.join(DATA, "pages")
    for f in sorted(glob.glob(os.path.join(src, "*.jsonl"))):
        for line in open(f):
            try:
                j = json.loads(line)
            except ValueError:
                continue
            m = j["ts"][:6]
            if not (START <= m <= END):
                continue
            pk = (j["url"].split("#")[0], m)
            if pk in seen_pages:   # same URL in same month from CC and Wayback: count once
                continue
            seen_pages.add(pk)
            reg = j["region"]
            c = pages[(reg, m)]
            c["pages_fetched"] += 1
            if j.get("n", 0) <= 0:
                continue
            c["pages_with_products"] += 1
            c["src_" + j.get("src", "?")] += 1
            c["fmt_" + j.get("fmt", "?")] += 1
            for p in j["products"]:
                o, pr = p["orig"], p["price"]
                if pr > o * 1.01 or pr <= 0:      # bad pair
                    continue
                d = max(0.0, 1 - pr / o)
                if d > 0.9:
                    continue
                key = (reg, m, j.get("fmt"), p.get("sku") or p.get("name"))
                prods[key].append(d)
                meta[key] = (j.get("country"), is_nike(p.get("name"), p.get("brand")))
                c["product_obs"] += 1

    agg = defaultdict(lambda: [0, 0, 0.0, 0.0])          # n, n_sale, sum_disc, sum_disc_sale
    for key, ds in prods.items():
        reg, m, fmt, _ = key
        cty, nike = meta[key]
        d = sum(ds) / len(ds)
        sale = d > 0.005
        for seg in ("all", "fmt_" + str(fmt), "nike_jordan" if nike else "non_nike", "country_" + str(cty)):
            a = agg[(reg, m, seg)]
            a[0] += 1
            a[1] += sale
            a[2] += d
            a[3] += d if sale else 0
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "monthly_metrics.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["region", "month", "segment", "products", "pct_on_sale", "avg_disc_all", "avg_disc_on_sale"])
        for (reg, m, seg), (n, ns, sd, sds) in sorted(agg.items()):
            w.writerow([reg, m[:4] + "-" + m[4:], seg, n, round(ns / n, 4), round(sd / n, 4),
                        round(sds / ns, 4) if ns else ""])
    cols = ["pages_fetched", "pages_with_products", "src_cc", "src_wb", "fmt_cat", "fmt_seo", "fmt_rx", "product_obs"]
    months = []
    y, mo = int(START[:4]), int(START[4:])
    while "%04d%02d" % (y, mo) <= END:
        months.append("%04d%02d" % (y, mo))
        y, mo = (y + 1, 1) if mo == 12 else (y, mo + 1)
    with open(os.path.join(OUT, "pages_per_month.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["region", "month"] + cols)
        for reg in ("NA", "EMEA"):
            for m in months:
                c = pages.get((reg, m), {})
                w.writerow([reg, m[:4] + "-" + m[4:]] + [c.get(k, 0) for k in cols])
    for reg in ("NA", "EMEA"):
        v = [pages.get((reg, m), {}).get("pages_with_products", 0) for m in months]
        print("%s pages-with-products/month: avg %.0f, min %d, months>=2000: %d/%d"
              % (reg, sum(v) / len(v), min(v), sum(x >= 2000 for x in v), len(v)))
        print("  " + " ".join("%s:%d" % (m[2:], x) for m, x in zip(months, v)))


if __name__ == "__main__":
    main()
