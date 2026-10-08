"""Weekly Foot Locker catalog census (runs W01_census.py + W01_census_champs.py, then summarizes).

Usage: python3 scripts/weekly_fl.py [--skip-census]
Appends dated rows to:
  data/weekly/FL_pages.csv  - top-level pages on footlocker.com, champssports.com, kidsfootlocker.com, footlocker.ca:
                              total listings, Sale facet count, sale share, first-page (48) discount depth on sale items
  data/weekly/FL_brand.csv  - per site x collection x brand: listings, on-sale listings, sale share,
                              median / mean discount depth of sampled on-sale items
Holiday benchmark (Dec 2025, Wayback): footlocker.com sale page 2,608-2,866 items at 42-47% first-page depth.
"""
import csv, datetime as dt, json, os, statistics as st, subprocess, sys
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(R, "scripts"))
import W01_fetch as F

TODAY = dt.date.today().isoformat()
OUT = os.path.join(R, "data", "weekly"); os.makedirs(OUT, exist_ok=True)
os.makedirs(os.path.join(R, "raw", "W01"), exist_ok=True)

def append(name, rows):
    if not rows: return
    path = os.path.join(OUT, name); new = not os.path.exists(path)
    with open(path, "a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        if new: w.writeheader()
        w.writerows(rows)

def disc(p):
    try:
        o = p["originalPrice"]["value"]; pr = p["price"]["value"]
        return 100 * (o - pr) / o if o and pr < o - 0.005 else 0.0
    except Exception:
        return None

# 1) top-level pages
prow = []
for dom in ["footlocker.com", "champssports.com", "kidsfootlocker.com", "footlocker.ca"]:
    for path in ["/category/mens/shoes.html", "/category/womens/shoes.html", "/category/kids/shoes.html", "/category/shoes.html", "/category/sale.html"]:
        t = F.get("https://www.%s%s" % (dom, path))
        if not t: print(dom, path, "FAIL"); continue
        pg, fac, pr = F.parse(t)
        if not pg: print(dom, path, "noobj"); continue
        misc = {}
        for x in fac or []:
            if x["code"] in ("miscellaneous", "saleProduct", "sale"):
                misc.update({v["name"]: v["count"] for v in x["values"]})
        tot = pg.get("totalResults"); sale = misc.get("Sale Product", misc.get("Sale"))
        if path.endswith("sale.html") and sale is None: sale = tot
        ds = [d for d in (disc(p) for p in (pr or [])) if d]
        prow.append(dict(date=TODAY, site=dom, page=path, total=tot, sale=sale,
                         sale_share=round(sale / tot, 4) if sale and tot else "",
                         p1_on_sale=len(ds), p1_depth_mean=round(st.mean(ds), 1) if ds else "",
                         p1_depth_median=round(st.median(ds), 1) if ds else ""))
        print(prow[-1], flush=True)
append("FL_pages.csv", prow)

# 2) full brand census (~12 min per site)
if "--skip-census" not in sys.argv:
    for s in ["W01_census.py", "W01_census_champs.py"]:
        subprocess.run([sys.executable, os.path.join(R, "scripts", s)], check=False)

def summarize(site, counts_file, prod_file):
    cf = os.path.join(R, "raw", "W01", counts_file); pf = os.path.join(R, "raw", "W01", prod_file)
    if not (os.path.exists(cf) and os.path.exists(pf)): return []
    depth = {}
    for l in open(pf):
        d = json.loads(l)
        if d["slice"] != "sale": continue
        x = disc(d["p"])
        if x: depth.setdefault((d["coll"], d["brand"]), []).append(x)
    rows = []
    for r in csv.DictReader(open(cf)):
        tot = int(r["total"]) if r["total"] not in ("", "None") else None
        sal = int(r["sale_total"]) if r["sale_total"] not in ("", "None") else 0
        ds = depth.get((r["collection"], r["brand"]), [])
        rows.append(dict(date=TODAY, site=site, collection=r["collection"], brand=r["brand"], listings=tot, on_sale=sal,
                         sale_share=round(sal / tot, 4) if tot else "", depth_n=len(ds),
                         depth_median=round(st.median(ds), 1) if ds else "", depth_mean=round(st.mean(ds), 1) if ds else ""))
    return rows

brows = summarize("footlocker.com", "brand_counts.csv", "products.jsonl") + summarize("champssports.com", "champs_brand_counts.csv", "champs_products.jsonl")
append("FL_brand.csv", brows)
for site in ("footlocker.com", "champssports.com"):
    for coll in sorted({r["collection"] for r in brows if r["site"] == site}):
        rs = [r for r in brows if r["site"] == site and r["collection"] == coll and r["listings"]]
        L = sum(r["listings"] for r in rs); S = sum(r["on_sale"] for r in rs)
        print(TODAY, site, coll, "listings", L, "on_sale", S, "share %.1f%%" % (100 * S / L if L else 0))
