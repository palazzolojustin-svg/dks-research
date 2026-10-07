"""X11 step 4: deeper cuts on the Common Crawl product file.
Rerun: python X11_cc_deep.py [crawl ...]   (default: all crawls with product files)
Prints: per-owned-brand on-sale share; matched-category price points (median list/offer)
owned vs national; persistence of markdowns for products seen in >=3 crawls; new-SKU
(dsgProductSortDate) counts by month for owned vs national.
Writes PB_SCRAPE/raw/X11_brand_sale_by_crawl.csv, X11_pricepoints.csv, X11_newsku_by_month.csv
"""
import csv, glob, json, os, sys, statistics as st, collections

RAW = os.path.join(os.path.dirname(__file__), "..", "raw")
CC = os.path.join(RAW, "X11_cc")


def f(x):
    try:
        return float(x)
    except Exception:
        return None


def owned(r):
    return bool(r.get("vb")) and "Vertical Brand" in r["vb"]


def onsale(r):
    return f(r["list"]) and f(r["offer"]) is not None and f(r["offer"]) < f(r["list"]) - 0.005


def load(cid):
    rows = {}
    for l in open(os.path.join(CC, cid + "_products.jsonl"), encoding="utf-8"):
        r = json.loads(l)
        if r["pp"] and r["pp"] not in rows:
            rows[r["pp"]] = r
    return rows


crawls = sys.argv[1:] or sorted({os.path.basename(p).split("_")[0] for p in glob.glob(os.path.join(CC, "*_products.jsonl"))})
data = {c: load(c) for c in crawls}
data = {c: v for c, v in data.items() if v}

# 1 per brand
BR = ["CALIA", "DSG", "VRST", "Maxfli", "Walter Hagen", "Alpine Design", "ETHOS", "Fitness Gear", "Nishiki", "Quest", "Top Flite",
      "Nike", "Under Armour", "adidas", "Jordan", "New Balance", "The North Face", "Columbia", "Vuori", "Titleist", "Callaway", "TaylorMade", "PUMA", "Brooks", "HOKA", "On"]
rows = []
for c, d in data.items():
    for b in BR:
        rs = [r for r in d.values() if r["brand"] == b]
        if len(rs) >= 15:
            s = [r for r in rs if onsale(r)]
            dep = [1 - f(r["offer"]) / f(r["list"]) for r in s]
            rows.append(dict(crawl=c, brand=b, n=len(rs), on_sale=round(len(s) / len(rs), 3),
                             depth=round(st.mean(dep), 3) if dep else 0, med_list=st.median([f(r["list"]) for r in rs if f(r["list"])]),
                             med_offer=st.median([f(r["offer"]) for r in rs if f(r["offer"])])))
with open(os.path.join(RAW, "X11_brand_sale_by_crawl.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print("=== per brand")
for r in rows: print(r)

# 2 price points by product type (latest crawl pooled with previous 3)
pool = {}
for c in list(data)[-4:]:
    for k, r in data[c].items():
        pool.setdefault(k, r)
TYPES = ["Leggings", "Pants", "Joggers", "Shorts", "Shirts", "Sweatshirts", "Hoodies", "Jackets", "Sports Bras", "Golf Balls", "Polos", "Tights"]
pp = []
for t in TYPES:
    for g in ("Women's", "Men's", None):
        sel = [r for r in pool.values() if r.get("ptype") and t in r["ptype"] and (g is None or (r.get("gender") and g in r["gender"]))]
        if g is None and t not in ("Golf Balls",):
            continue
        o = [r for r in sel if owned(r)]; n = [r for r in sel if not owned(r)]
        if len(o) >= 8 and len(n) >= 8:
            def m(x, k): v = [f(r[k]) for r in x if f(r[k])]; return round(st.median(v), 2) if v else None
            pp.append(dict(type=t, gender=g or "all", owned_n=len(o), nat_n=len(n), owned_med_list=m(o, "list"), owned_med_offer=m(o, "offer"),
                           nat_med_list=m(n, "list"), nat_med_offer=m(n, "offer"),
                           owned_on_sale=round(sum(map(bool, map(onsale, o))) / len(o), 3), nat_on_sale=round(sum(map(bool, map(onsale, n))) / len(n), 3)))
with open(os.path.join(RAW, "X11_pricepoints.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(pp[0].keys())); w.writeheader(); w.writerows(pp)
print("=== price points (pooled latest 4 crawls)")
for r in pp: print(r)

# 3 persistence
seen = collections.defaultdict(list)
for c, d in data.items():
    for k, r in d.items():
        seen[k].append(r)
for lab, fn in (("owned", owned), ("national", lambda r: not owned(r))):
    multi = [v for v in seen.values() if len(v) >= 3 and fn(v[0])]
    always = [v for v in multi if all(onsale(r) for r in v)]
    never = [v for v in multi if not any(onsale(r) for r in v)]
    print("persistence", lab, "products seen>=3 crawls", len(multi), "always on sale", round(len(always) / max(1, len(multi)), 3), "never on sale", round(len(never) / max(1, len(multi)), 3))

# 4 new SKU sort dates by month (product first-set dates), owned share
allp = {}
for d in data.values():
    for k, r in d.items():
        allp.setdefault(k, r)
cnt = collections.defaultdict(lambda: [0, 0])
for r in allp.values():
    sd = r.get("sortdate") or ""
    if len(sd) == 10:
        ym = sd[6:10] + "-" + sd[0:2]
        cnt[ym][0 if owned(r) else 1] += 1
out = [dict(month=k, owned=v[0], national=v[1], owned_share=round(v[0] / (v[0] + v[1]), 3)) for k, v in sorted(cnt.items()) if k >= "2023-01"]
with open(os.path.join(RAW, "X11_newsku_by_month.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["month", "owned", "national", "owned_share"]); w.writeheader(); w.writerows(out)
print("=== product sort date by month (unique products in sample)")
for r in out: print(r)
