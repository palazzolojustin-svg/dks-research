"""X11 step 3: owned (DKS 'Vertical Brand') vs national markdown metrics by Common Crawl crawl.

Rerun:  python X11_cc_analyze.py      (after X11_cc_index.py and X11_cc_extract.py)
Outputs (PB_SCRAPE/raw/):
  X11_sku_sale_by_crawl.csv     SKU-level on-sale share & discount depth, owned vs national, per crawl
  X11_matched_cat_by_crawl.csv  same, within matched product categories (owned-weighted)
  X11_brandpage_sale.csv        whole-assortment 'Sale' facet / totalCount on brand landing pages
  X11_brandfacet_panel.csv      owned-brand share of brand-facet SKU counts on generic category pages
  X11_pricepoints.csv           median list price by category, owned vs national (latest crawl)
Definitions:
  owned = product attribute 6025 == 'Vertical Brand' (DKS's own tag), else national.
  on_sale = displayed SKU offer price < list price (by >=1 cent).
  any_md  = min offer price across SKUs < max list price (some colour/size marked down).
  depth   = 1 - offer/list on the displayed SKU (mean over on-sale products).
Products deduped by parent part number within each crawl (first capture kept).
"""
import csv, glob, json, os, re, statistics as st, collections

RAW = os.path.join(os.path.dirname(__file__), "..", "raw")
CC = os.path.join(RAW, "X11_cc")
CRAWL_MONTH = {}
OWNED_SLUGS = ["calia", "dsg", "vrst", "maxfli", "walter-hagen", "top-flite", "tommy-armour",
               "alpine-design", "ethos", "fitness-gear", "nishiki", "quest"]
NAT_SLUGS = ["nike", "under-armour", "adidas", "new-balance", "the-north-face", "columbia",
             "vuori", "titleist", "callaway", "taylormade", "jordan", "puma", "brooks", "hoka", "on-"]


def f(x):
    try:
        return float(x)
    except Exception:
        return None


def load(cid):
    rows = {}
    p = os.path.join(CC, cid + "_products.jsonl")
    if not os.path.exists(p):
        return []
    for l in open(p, encoding="utf-8"):
        r = json.loads(l)
        if r["pp"] and r["pp"] not in rows:
            rows[r["pp"]] = r
    return list(rows.values())


def metrics(rs):
    n = len(rs)
    if not n:
        return dict(n=0)
    sale = [r for r in rs if f(r["list"]) and f(r["offer"]) is not None and f(r["offer"]) < f(r["list"]) - 0.005]
    anym = [r for r in rs if f(r["maxlist"]) and f(r["minoffer"]) is not None and f(r["minoffer"]) < f(r["maxlist"]) - 0.005]
    depth = [1 - f(r["offer"]) / f(r["list"]) for r in sale]
    lists = [f(r["list"]) for r in rs if f(r["list"])]
    return dict(n=n, on_sale=len(sale) / n, any_md=len(anym) / n,
                depth_on_sale=(st.mean(depth) if depth else 0),
                avg_disc_all=sum(depth) / n, med_list=(st.median(lists) if lists else None))


def owned(r):
    return bool(r.get("vb")) and "Vertical Brand" in r["vb"]


def main():
    crawls = sorted({os.path.basename(p).split("_")[0] for p in glob.glob(os.path.join(CC, "*_products.jsonl"))})
    out = []
    mc = []
    for cid in crawls:
        rs = load(cid)
        ts = sorted(r["ts"] for r in rs)
        mid = ts[len(ts) // 2][:8] if ts else ""
        o = [r for r in rs if owned(r)]; nn = [r for r in rs if not owned(r)]
        mo, mn = metrics(o), metrics(nn)
        out.append(dict(crawl=cid, median_capture=mid, owned_n=mo["n"], nat_n=mn["n"],
                        owned_on_sale=round(mo.get("on_sale", 0), 4), nat_on_sale=round(mn.get("on_sale", 0), 4),
                        owned_any_md=round(mo.get("any_md", 0), 4), nat_any_md=round(mn.get("any_md", 0), 4),
                        owned_depth=round(mo.get("depth_on_sale", 0), 4), nat_depth=round(mn.get("depth_on_sale", 0), 4),
                        owned_avg_disc=round(mo.get("avg_disc_all", 0), 4), nat_avg_disc=round(mn.get("avg_disc_all", 0), 4)))
        # matched categories
        bycat = collections.defaultdict(lambda: [[], []])
        for r in rs:
            if r["cat"]:
                bycat[r["cat"]][0 if owned(r) else 1].append(r)
        wo = wn = wdo = wdn = w = 0
        for cat, (a, b) in bycat.items():
            if len(a) >= 5 and len(b) >= 5:
                ma, mb = metrics(a), metrics(b)
                k = len(a); w += k
                wo += k * ma["on_sale"]; wn += k * mb["on_sale"]
                wdo += k * ma["avg_disc_all"]; wdn += k * mb["avg_disc_all"]
        if w:
            mc.append(dict(crawl=cid, median_capture=mid, owned_weight=w, owned_on_sale=round(wo / w, 4),
                           nat_on_sale=round(wn / w, 4), owned_avg_disc=round(wdo / w, 4), nat_avg_disc=round(wdn / w, 4)))
    with open(os.path.join(RAW, "X11_sku_sale_by_crawl.csv"), "w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(out[0].keys())); wr.writeheader(); wr.writerows(out)
    if mc:
        with open(os.path.join(RAW, "X11_matched_cat_by_crawl.csv"), "w", newline="") as fh:
            wr = csv.DictWriter(fh, fieldnames=list(mc[0].keys())); wr.writeheader(); wr.writerows(mc)
    for r in out: print(r)
    print("--- matched categories")
    for r in mc: print(r)

    # brand landing pages: whole-assortment sale share
    bp = []
    for p in sorted(glob.glob(os.path.join(CC, "*_pages.jsonl"))):
        cid = os.path.basename(p).split("_")[0]
        for l in open(p, encoding="utf-8"):
            g = json.loads(l)
            if not g.get("totalCount"):
                continue
            slug = g["url"].split("/f/")[-1].lower()
            grp = None
            for s in OWNED_SLUGS:
                if slug.startswith(s + "-") or slug == s:
                    grp = ("owned", s)
            for s in NAT_SLUGS:
                if slug.startswith(s if s.endswith("-") else s + "-") or slug == s.strip("-"):
                    grp = ("national", s.strip("-"))
            if grp:
                bp.append(dict(crawl=cid, ts=g["ts"], url=g["url"], group=grp[0], brand=grp[1],
                               total=g["totalCount"], sale=g.get("sale_count") or 0))
    with open(os.path.join(RAW, "X11_brandpage_sale.csv"), "w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=["crawl", "ts", "url", "group", "brand", "total", "sale"]); wr.writeheader(); wr.writerows(bp)
    print("--- brand pages (pooled: sum sale / sum total)")
    agg = collections.defaultdict(lambda: [0, 0, 0])
    for r in bp:
        a = agg[(r["crawl"], r["group"])]; a[0] += r["sale"]; a[1] += r["total"]; a[2] += 1
    for k in sorted(agg):
        a = agg[k]; print(k, "pages", a[2], "sale", a[0], "total", a[1], "share", round(a[0] / a[1], 3) if a[1] else None)

    # brand facet: owned share of SKU counts on generic category pages
    OWN_FACET = {"CALIA", "DSG", "VRST", "Maxfli", "Walter Hagen", "Top Flite", "Tommy Armour Golf", "Tommy Armour",
                 "Alpine Design", "ETHOS", "Fitness Gear", "Nishiki", "Quest", "P-TEX", "DBX", "Northeast Outfitters",
                 "DICK'S Sporting Goods", "Slazenger", "PRIMED", "TourTrek", "Jawbone"}
    pan = []
    for p in sorted(glob.glob(os.path.join(CC, "*_pages.jsonl"))):
        cid = os.path.basename(p).split("_")[0]
        for l in open(p, encoding="utf-8"):
            g = json.loads(l)
            b = ((g.get("facets") or {}).get("Brand") or {}).get("vals")
            if not b or len(b) < 3:
                continue
            tot = sum(b.values()); ow = sum(v for k, v in b.items() if k in OWN_FACET)
            pan.append(dict(crawl=cid, ts=g["ts"], url=g["url"], total=tot, owned=ow, totalCount=g.get("totalCount"),
                            sale=g.get("sale_count") or 0))
    with open(os.path.join(RAW, "X11_brandfacet_panel.csv"), "w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=["crawl", "ts", "url", "total", "owned", "totalCount", "sale"]); wr.writeheader(); wr.writerows(pan)


if __name__ == "__main__":
    main()
