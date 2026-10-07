"""R9 step 3: analyse Common Crawl dicks.com listing captures → owned-brand ('Vertical Brand') share
of listings, of new SKUs, of first-row slots, of DKS 'TopSeller' badges, of Bazaarvoice review counts,
plus owned-brand full-price (not-on-markdown) share by brand, per crawl and per period.

Rerun:  python R9_cc_analyze.py [tag=dks]
Inputs:  raw/R9/cc/<crawl>_<tag>_products.jsonl + _pages.jsonl   (R9_cc_extract.py)
         raw/X11_cc/<crawl>_products.jsonl (X11, 2025-08 → 2026-09; no review counts/badges; pooled for
         listing-share and price metrics where present; positions re-derived from file order)
Outputs: raw/R9_crawl_summary.csv, raw/R9_owned_share_by_cat.csv, raw/R9_brand_price.csv,
         raw/R9_period_summary.txt (human-readable)
Definitions
  owned = DKS attribute 6025 'Vertical Brand' present AND brand not a licensed brand (Lotto, adidas,
          Cobra, Marucci). FanShop (league/college licensed) categories are excluded everywhere.
  random page = page URL does not contain any priority brand/category slug (unbiased sample).
  mixed page = >=4 distinct brands among listed products.
  new SKU = dsgProductSortDate within 183 days before capture date.
  on sale = displayed SKU offer < list price (both > 0).
"""
import collections, csv, datetime as dt, glob, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from R9_cc_common import RAW

TAG = sys.argv[1] if len(sys.argv) > 1 else "dks"
PRIORITY = ["calia", "dsg", "vrst", "maxfli", "walter-hagen", "top-flite", "tommy-armour",
            "alpine-design", "ethos", "fitness-gear", "nishiki", "quest", "nike", "under-armour",
            "adidas", "new-balance", "the-north-face", "columbia", "vuori", "lululemon", "titleist",
            "callaway", "taylormade", "leggings", "joggers", "golf-balls", "hoodies", "fleece",
            "shorts", "t-shirts", "tees"]
OWNED_SLUGS = ["calia", "dsg", "vrst", "maxfli", "walter-hagen", "top-flite", "tommy-armour", "alpine-design",
               "ethos", "fitness-gear", "nishiki", "quest", "exclusive", "dbx", "p-tex", "primed"]
LICENSED = {"lotto", "adidas", "cobra", "marucci", "cobra golf"}
FAN = re.compile(r"^(NCAA|NFL|MLB|NBA|NHL|MLS|WNBA|NWSL|International|National|MiLB|ESPN|Hidden|PLL|Olympic|USA|Collegiate|F1|Fan)")
FOOT = re.compile(r"(Cleats|Running$|Sneakers|SlidesSandals|Sandals|Boots|CrossTraining|Tennis$|WrestlingShoes|^MensBasketball$|^WomensBasketball$|^WomensTraining$|^MensTraining$|Hiking|Shoes|Slippers|Walking|Clogs|Turf|Spikes)")
GOLF = re.compile(r"^(Golf|IronSets|Drivers|Putters|Wedges|Hybrids|FairwayWoods|CompleteSets|UsedDemos|Mens Golf|WomensGolf|MensGolf)")
FIT = re.compile(r"(Dumbbell|Exercise|Treadmill|Elliptical|Resistance|Weight|Bench|Kettlebell|Fitness|Rowing|Yoga|Foam|Barbell|Plates|SmithMachine|HomeGym|Recovery|Massage|HandWristBody|WorkoutGloves|JumpRopes|Ab|Strength|Cardio|Pilates|Bands)")
OUT = re.compile(r"(Bike|Camp|Tent|Cooler|Kayak|Canoe|Fishing|Fly|Hunting|Sleeping|Chair|Hammock|Grill|Lantern|Hydration|Paddle|LifeVest|Shelter|Lure|Bait|Reel|Rod|Sinker|Ice|Archery|Knife|Knives|Optics|Binocular|Waders|Air Mattress|AirMattress|Climbing|Snow|Ski|Scooter|Skate|Pool|Water|Swim(?!suits))")
TEAM = re.compile(r"(Baseball|Softball|Lacrosse|Hockey|Football|Soccer|Basketballs|Volleyball|Batting|Bat|Catcher|Mouthguard|Goal|Rebound|Pickleball|TennisRackets|Racquet|Wrestling|Cheer|Referee|Kickball)")
ACC = re.compile(r"^(Hats|Socks|Gloves|Belts|Headbands|Sunglasses|BackpacksDuffles|WaterBottles|Bags|NeckGaiters|Insoles|BracesSupport|Watches|ActivityTrackers|Skincare|Hair|Wallets|Headphones|Masks)")
CORE = ["DSG", "CALIA", "VRST", "Maxfli", "Walter Hagen"]


def catgroup(cat):
    c = (cat or "").split("-")[0]
    if not c:
        return "UNK"
    if FAN.search(c):
        return "FAN"
    if FOOT.search(c):
        return "FOOTWEAR"
    if c.startswith("GolfBalls"):
        return "GOLFBALLS"
    if GOLF.search(c):
        return "GOLF"
    if re.match(r"^(Womens|Women)", c):
        return "W_APP"
    if re.match(r"^(Mens|Men)", c):
        return "M_APP"
    if re.match(r"^(Boys|Girls|Kids|Youth|Toddler|Infant)", c):
        return "K_APP"
    if ACC.search(c):
        return "ACC"
    if FIT.search(c):
        return "FIT"
    if TEAM.search(c):
        return "TEAM"
    if OUT.search(c):
        return "OUTDOOR"
    return "OTHER"


def is_owned(r):
    return bool(r.get("vb")) and (r.get("brand") or "").strip().lower() not in LICENSED


def bgroup(r):
    b = (r.get("brand") or "").strip()
    if not is_owned(r):
        return "NATIONAL"
    if b in ("Walter Hagen", "Lady Hagen"):
        return "Walter Hagen"
    if b in CORE:
        return b
    return "OTHER_OWNED"


def ts2d(ts):
    return dt.datetime.strptime(ts[:8], "%Y%m%d").date()


def sd2d(s):
    try:
        return dt.datetime.strptime(s, "%m/%d/%Y").date()
    except Exception:
        return None


def is_random(url):
    u = url.lower()
    return not any(("/f/" + s) in u or ("-" + s) in u for s in PRIORITY)


def is_owned_page(url):
    u = url.lower()
    return any(("/f/" + s) in u or ("-" + s + "-") in u or u.endswith("-" + s) for s in OWNED_SLUGS)


def load():
    rows = collections.defaultdict(list)  # crawl -> list
    src = {}
    for f in sorted(glob.glob(os.path.join(RAW, "R9", "cc", f"*_{TAG}_products.jsonl"))):
        c = os.path.basename(f)[:15]
        for l in open(f, encoding="utf-8"):
            try:
                r = json.loads(l)
            except Exception:
                continue
            r["src"] = "R9"
            rows[c].append(r)
        src[c] = "R9"
    # X11 fallback / pool (same sampling rule). Re-derive positions.
    for f in (sorted(glob.glob(os.path.join(RAW, "X11_cc", "*_products.jsonl"))) if TAG == "dks" else []):
        c = os.path.basename(f)[:15]
        have = {r["page"] for r in rows.get(c, [])}
        last, pos = None, 0
        for l in open(f, encoding="utf-8"):
            try:
                r = json.loads(l)
            except Exception:
                continue
            if r["page"] != last:
                last, pos = r["page"], 0
            pos += 1
            if r["page"] in have:
                continue
            r["pos"], r["src"], r["rc"], r["badge"] = pos, "X11", None, None
            rows[c].append(r)
        src[c] = src.get(c, "") + "+X11"
    return rows, src


def share(num, den):
    return round(100.0 * num / den, 2) if den else None


def main():
    rows, src = load()
    summ, bycat, bprice = [], [], []
    for c in sorted(rows):
        R = [r for r in rows[c] if catgroup(r.get("cat")) != "FAN"]
        if not R:
            continue
        dates = sorted(ts2d(r["ts"]) for r in R)
        d0 = dates[len(dates) // 2]
        pages = collections.defaultdict(list)
        for r in R:
            pages[r["page"]].append(r)
        # unique products (all pages)
        U = {}
        for r in R:
            U.setdefault(r["pp"], r)
        Urand = {}
        for r in R:
            if is_random(r["page"]):
                Urand.setdefault(r["pp"], r)
        slots_rand = [r for r in R if is_random(r["page"])]
        mixed = [p for p, L in pages.items() if len({x.get("brand") for x in L}) >= 4 and not is_owned_page(p)]
        top12 = [r for p in mixed for r in pages[p] if (r.get("pos") or 99) <= 12]
        allmixed = [r for p in mixed for r in pages[p]]
        newsku = [r for r in U.values() if sd2d(r.get("sortdate") or "") and 0 <= (d0 - sd2d(r["sortdate"])).days <= 183]
        newsku_r = [r for r in Urand.values() if sd2d(r.get("sortdate") or "") and 0 <= (d0 - sd2d(r["sortdate"])).days <= 183]
        tops = [r for r in U.values() if r.get("badge") == "TopSeller"]
        newarr = [r for r in U.values() if r.get("badge") == "NewArrivals"]
        rcU = [r for r in Urand.values() if isinstance(r.get("rc"), (int, float))]
        rc_own = sum(r["rc"] for r in rcU if is_owned(r)); rc_all = sum(r["rc"] for r in rcU)
        row = {"crawl": c, "median_capture": d0.isoformat(), "src": src.get(c), "pages": len(pages),
               "rand_pages": sum(1 for p in pages if is_random(p)), "mixed_pages": len(mixed),
               "uniq_products": len(U), "owned_uniq_pct": share(sum(is_owned(r) for r in U.values()), len(U)),
               "rand_uniq": len(Urand), "owned_rand_uniq_pct": share(sum(is_owned(r) for r in Urand.values()), len(Urand)),
               "rand_slots": len(slots_rand), "owned_rand_slots_pct": share(sum(is_owned(r) for r in slots_rand), len(slots_rand)),
               "mixed_slots": len(allmixed), "owned_mixed_slots_pct": share(sum(is_owned(r) for r in allmixed), len(allmixed)),
               "top12_slots": len(top12), "owned_top12_pct": share(sum(is_owned(r) for r in top12), len(top12)),
               "newsku_n": len(newsku), "owned_newsku_pct": share(sum(is_owned(r) for r in newsku), len(newsku)),
               "newsku_rand_n": len(newsku_r), "owned_newsku_rand_pct": share(sum(is_owned(r) for r in newsku_r), len(newsku_r)),
               "topseller_n": len(tops), "owned_topseller_pct": share(sum(is_owned(r) for r in tops), len(tops)),
               "newarrival_n": len(newarr), "owned_newarrival_pct": share(sum(is_owned(r) for r in newarr), len(newarr)),
               "rc_products": len(rcU), "owned_reviewcount_pct": share(rc_own, rc_all),
               "owned_median_rc": sorted(r["rc"] for r in rcU if is_owned(r))[len([1 for r in rcU if is_owned(r)]) // 2] if any(is_owned(r) for r in rcU) else None,
               "natl_median_rc": sorted(r["rc"] for r in rcU if not is_owned(r))[len([1 for r in rcU if not is_owned(r)]) // 2] if any(not is_owned(r) for r in rcU) else None}
        summ.append(row)
        # by category (unique products, all pages; and random-only)
        g = collections.defaultdict(lambda: [0, 0, 0, 0])
        for r in U.values():
            k = catgroup(r.get("cat")); g[k][0] += 1; g[k][1] += is_owned(r)
        for r in Urand.values():
            k = catgroup(r.get("cat")); g[k][2] += 1; g[k][3] += is_owned(r)
        for k, (n, o, nr, orr) in sorted(g.items()):
            bycat.append({"crawl": c, "median_capture": d0.isoformat(), "catgroup": k, "uniq": n, "owned_pct": share(o, n),
                          "rand_uniq": nr, "owned_rand_pct": share(orr, nr)})
        # price by brand group (unique products)
        b = collections.defaultdict(list)
        for r in U.values():
            try:
                L, O = float(r.get("list") or 0), float(r.get("offer") or 0)
            except Exception:
                continue
            if L > 0 and O > 0:
                b[bgroup(r)].append((L, O, catgroup(r.get("cat"))))
        for k, v in sorted(b.items()):
            sale = [1 if O < L - 0.005 else 0 for L, O, _ in v]
            disc = [max(0.0, 1 - O / L) for L, O, _ in v]
            ond = [d for d, s in zip(disc, sale) if s]
            offers = sorted(O for _, O, _ in v)
            bprice.append({"crawl": c, "median_capture": d0.isoformat(), "brand": k, "n": len(v),
                           "onsale_pct": share(sum(sale), len(v)), "fullprice_pct": share(len(v) - sum(sale), len(v)),
                           "avg_disc_pct": round(100 * sum(disc) / len(v), 2),
                           "depth_when_on_sale_pct": round(100 * sum(ond) / len(ond), 2) if ond else None,
                           "median_offer": offers[len(offers) // 2]})
    for name, data in (("R9_crawl_summary.csv", summ), ("R9_owned_share_by_cat.csv", bycat), ("R9_brand_price.csv", bprice)):
        if data:
            if TAG != "dks":
                name = name.replace("R9_", f"R9_{TAG}_")
            with open(os.path.join(RAW, name), "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=list(data[0].keys())); w.writeheader(); w.writerows(data)
    for r in summ:
        print({k: r[k] for k in ("crawl", "median_capture", "src", "pages", "uniq_products", "owned_uniq_pct", "owned_rand_uniq_pct",
                                 "owned_rand_slots_pct", "owned_mixed_slots_pct", "owned_top12_pct", "owned_newsku_pct",
                                 "owned_topseller_pct", "topseller_n", "owned_newarrival_pct", "owned_reviewcount_pct", "rc_products")})


if __name__ == "__main__":
    main()
