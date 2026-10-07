"""X02: analyze a dicks.com catalog census CSV produced by X02_census_browser.js.

Rerun: python PB_SCRAPE\\scripts\\X02_analyze_census.py PB_SCRAPE\\raw\\X02_dsg_products_<date>.csv
Metrics per category and in total (owned = DKS attribute 6025 'Vertical Brand' OR brand in OWNED list):
  products, owned share of listed products; owned share of Top-Sellers top-24/48/144; owned share of
  New-Products top-48; % of products on sale (offer < list) and avg discount, owned vs national;
  launch-date (attr 4474) month histogram owned vs national; review-count share.
Writes PB_SCRAPE\\raw\\X02_census_summary_<date>.csv and X02_census_launch_months_<date>.csv
"""
import sys, os, csv, collections, statistics, datetime

OWNED = {"DSG", "CALIA", "VRST", "MAXFLI", "Maxfli", "Walter Hagen", "Top Flite", "Top-Flite", "Tommy Armour",
         "Alpine Design", "ETHOS", "Fitness Gear", "Nishiki", "Quest", "P-TEX", "PRIMED", "TourTrek", "DBX",
         "Jawbone", "THE SPORTS AUTHORITY", "Lady Hagen", "Field & Stream", "Slazenger"}
GROUP = {
    "womens-athletic-leggings": "W apparel", "sports-bras": "W apparel", "shop-womens-joggers": "W apparel",
    "womens-shorts-1": "W apparel", "womens-jackets-vests": "W apparel", "womens-shirts-tops": "W apparel",
    "mens-shorts": "M apparel", "mens-joggers": "M apparel", "mens-pants": "M apparel", "mens-shirts": "M apparel",
    "womens-golf-apparel": "Golf apparel", "mens-golf-apparel": "Golf apparel",
    "boys-shorts": "Kids apparel", "boys-shirts-tops": "Kids apparel", "girls-shirts-tops": "Kids apparel", "girls-leggings": "Kids apparel",
    "golf-balls": "Golf hardgoods", "golf-clubs": "Golf hardgoods", "putters": "Golf hardgoods", "golf-drivers": "Golf hardgoods",
    "golf-wedges": "Golf hardgoods", "golf-gloves": "Golf hardgoods", "golf-bags-accessories-1": "Golf hardgoods",
    "dumbbells": "Fitness", "weight-benches": "Fitness", "yoga-mats": "Fitness", "strength-training-equipment": "Fitness", "treadmills": "Fitness",
    "camping-coolers": "Outdoor", "camping-family-tents": "Outdoor", "sleeping-bags": "Outdoor", "water-bottles-hydration": "Outdoor",
    "backpacks-duffle-bags": "Outdoor", "bikes": "Outdoor",
    "baseball-bats": "Team sports", "baseball-gloves": "Team sports", "basketballs": "Team sports", "all-soccer-balls": "Team sports",
    "mens-running-shoes": "Footwear", "womens-running-shoes": "Footwear",
}


def f(x):
    try:
        return float(x)
    except Exception:
        return None


def is_owned(r):
    return r["vert"] == "1" or r["brand"] in OWNED


def main(path):
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    d = os.path.basename(path).split("_")[-1].replace(".csv", "")
    out = []
    vbrands = collections.Counter(r["brand"] for r in rows if r["vert"] == "1")
    nonflag_owned = collections.Counter(r["brand"] for r in rows if r["vert"] != "1" and r["brand"] in OWNED)
    print("brands carrying 6025 Vertical Brand flag:", vbrands.most_common())
    print("owned-list brands WITHOUT flag:", nonflag_owned.most_common())
    keys = list(dict.fromkeys(r["cat"] for r in rows))
    units = [(k, [k]) for k in keys] + [(g, [k for k in keys if GROUP.get(k) == g]) for g in dict.fromkeys(GROUP.values())] + [("ALL", keys)]
    hdr = ["unit", "products", "owned", "owned_pct", "top24_owned_pct", "top48_owned_pct", "top144_owned_pct", "new48_owned_pct",
           "owned_onsale_pct", "nat_onsale_pct", "owned_avg_disc_pct", "nat_avg_disc_pct", "owned_avg_list", "nat_avg_list",
           "owned_review_share", "owned_med_reviews", "nat_med_reviews", "owned_avg_rating", "nat_avg_rating"]
    for name, cats in units:
        if not cats:
            continue
        allr = {}
        for r in rows:
            if r["cat"] in cats and r["sort"] == "all":
                allr[(r["cat"], r["pid"])] = r
        A = list(allr.values())
        if not A:
            continue
        own = [r for r in A if is_owned(r)]; nat = [r for r in A if not is_owned(r)]

        def topshare(sort, n):
            t = [r for r in rows if r["cat"] in cats and r["sort"] == sort and int(r["rank"]) <= n]
            return round(100 * sum(is_owned(r) for r in t) / len(t), 1) if t else None

        def sale(lst):
            # "on sale" = the HIGHEST offer price is below the highest list price, i.e. every variant is marked down
            # (min-price comparison is distorted by single clearance colours)
            s = [r for r in lst if f(r["maxlist"]) and f(r["maxoffer"]) is not None]
            on = [r for r in s if f(r["maxoffer"]) < f(r["maxlist"]) - 0.005]
            disc = [100 * (1 - f(r["maxoffer"]) / f(r["maxlist"])) for r in on]
            lp = [f(r["maxlist"]) or f(r["minlist"]) for r in s]
            return (round(100 * len(on) / len(s), 1) if s else None, round(statistics.mean(disc), 1) if disc else None,
                    round(statistics.mean(lp), 2) if lp else None)

        so, sn = sale(own), sale(nat)
        rv_o = sum(f(r["bvn"]) or 0 for r in own); rv_n = sum(f(r["bvn"]) or 0 for r in nat)
        med = lambda L: statistics.median([f(r["bvn"]) or 0 for r in L]) if L else None
        rat = lambda L: round(statistics.mean([f(r["bvr"]) for r in L if f(r["bvr"])]), 2) if [r for r in L if f(r["bvr"])] else None
        out.append([name, len(A), len(own), round(100 * len(own) / len(A), 1), topshare("top", 24), topshare("top", 48), topshare("top", 144),
                    topshare("new", 48), so[0], sn[0], so[1], sn[1], so[2], sn[2],
                    round(100 * rv_o / (rv_o + rv_n), 1) if rv_o + rv_n else None, med(own), med(nat), rat(own), rat(nat)])
    with open(os.path.join(os.path.dirname(path), f"X02_census_summary_{d}.csv"), "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(hdr); w.writerows(out)
    for o in out:
        print(dict(zip(hdr, o)))
    # launch month histogram (attr 4474, MM/DD/YYYY) among currently listed products, deduped by pid
    seen = {}
    for r in rows:
        if r["sort"] == "all" and r["pid"] not in seen:
            seen[r["pid"]] = r
    mon = collections.defaultdict(lambda: [0, 0])
    for r in seen.values():
        dt = r["d4474"] or r["sortdate"]
        try:
            m = datetime.datetime.strptime(dt, "%m/%d/%Y").strftime("%Y-%m")
        except Exception:
            continue
        mon[m][0 if is_owned(r) else 1] += 1
    with open(os.path.join(os.path.dirname(path), f"X02_census_launch_months_{d}.csv"), "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["month", "owned", "national", "owned_pct"])
        for m in sorted(mon):
            o, n = mon[m]; w.writerow([m, o, n, round(100 * o / (o + n), 1)])
    print("launch months (owned, national, owned%):")
    for m in sorted(mon):
        if m >= "2024-01":
            o, n = mon[m]; print(m, o, n, round(100 * o / (o + n), 1))


if __name__ == "__main__":
    main(sys.argv[1])
