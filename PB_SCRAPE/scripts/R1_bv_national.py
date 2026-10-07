"""R1: pull NATIONAL-brand (and owned-brand refresh) reviews from the dicks.com Bazaarvoice front door.

Same access as X01 (no login, no passkey): header bv-bfd-token: 13107,main_site,en_US on
https://apps.bazaarvoice.com/bfd/v1/clients/dsg/api-products/cv2/resources/data/<products|reviews>.json

STEPS
  python R1_bv_national.py products            -> raw/R1_products_national.csv (all products with >=1 review for BRANDS)
  python R1_bv_national.py reviews             -> raw/R1_reviews_national.csv (every native review since 2023-01-01
                                                  on non-footwear products with last review >= 2023-01-01); resumable
  python R1_bv_national.py reviews Nike adidas -> only those brands
Extra review fields vs X01: last_moderated, POS (InStore/Online), OwnedFor, gender context.
Footwear products are skipped (owned brands have ~no footwear; keeps Nike/adidas pulls tractable).
Weekly rerun: delete raw/R1_reviews_national*.csv and *_done.txt, rerun both steps (~1-2h, 6 threads).
"""
import csv, os, re, sys, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, os.path.dirname(__file__))
from X01_bv_reviews import session_for, get, RAW

SINCE_EPOCH = 1672531200  # 2023-01-01
BRANDS = ["Under_Armour", "Nike", "Jordan", "adidas", "The_North_Face", "Columbia", "Champion", "Patagonia", "PUMA",
          "TravisMathew", "FootJoy", "Hurley", "Carhartt", "New_Balance", "FP_Movement", "Spyder", "Titleist",
          "Callaway", "TaylorMade", "Bridgestone", "Srixon", "PING", "Cobra", "Odyssey", "Wilson", "Rawlings",
          "Marucci", "Lotto", "Mizuno", "YETI", "Coleman", "Bowflex", "Brooks", "On", "Hoka"]
FOOTWEAR = re.compile(r"\b(shoes?|cleats?|slides?|sandals?|boots?|sneakers?|clogs?|flip[- ]?flops?|slippers?|trainers?|spikes)\b", re.I)
lock = threading.Lock()


def products(brands):
    s = session_for("dsg")
    path = os.path.join(RAW, "R1_products_national.csv")
    have = set()
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            have = {r["brand_id"] for r in csv.DictReader(f)}
    new = not os.path.exists(path)
    f = open(path, "a", newline="", encoding="utf-8"); w = csv.writer(f)
    if new:
        w.writerow(["product_id", "brand_id", "brand_name", "name", "category_id", "ancestry", "active",
                    "total_reviews", "avg_rating", "first_sub", "last_sub", "native_reviews"])
    for b in brands:
        if b in have:
            continue
        flt = [("Filter", f"BrandId:eq:{b}"), ("Filter", "TotalReviewCount:gte:1")]
        n = get(s, "dsg", "products", flt + [("Limit", "1")]).get("TotalResults") or 0
        print("products", b, n, flush=True)

        def page(o):
            return get(s, "dsg", "products", flt + [("Stats", "Reviews"), ("Limit", "100"), ("Offset", str(o))])
        with ThreadPoolExecutor(6) as ex:
            for r in ex.map(page, range(0, n, 100)):
                for x in r.get("Results", []):
                    st = x.get("ReviewStatistics") or {}
                    ns = x.get("NativeReviewStatistics") or {}
                    w.writerow([x["Id"], b, (x.get("Brand") or {}).get("Name"), x.get("Name"), x.get("CategoryId"),
                                "|".join(x.get("CategoryAncestryIds") or []), x.get("Active"), st.get("TotalReviewCount"),
                                st.get("AverageOverallRating"), st.get("FirstSubmissionTime"), st.get("LastSubmissionTime"),
                                ns.get("TotalReviewCount")])
        f.flush()
    f.close()


def reviews(only=None, ppath=None, rpath=None, dpath=None, skip_footwear=True):
    s = session_for("dsg")
    ppath = ppath or os.path.join(RAW, "R1_products_national.csv")
    rpath = rpath or os.path.join(RAW, "R1_reviews_national.csv")
    dpath = dpath or os.path.join(RAW, "R1_reviews_national_done.txt")
    with open(ppath, encoding="utf-8") as f:
        prods = [r for r in csv.DictReader(f) if r["last_sub"] and r["last_sub"][:10] >= "2023-01-01"
                 and (not only or r["brand_id"] in only)
                 and not (skip_footwear and FOOTWEAR.search(r["name"] or ""))]
    done = set(open(dpath, encoding="utf-8").read().split()) if os.path.exists(dpath) else set()
    prods = [p for p in prods if p["product_id"] not in done]
    print("products to fetch", len(prods), flush=True)
    new = not os.path.exists(rpath)
    f = open(rpath, "a", newline="", encoding="utf-8"); w = csv.writer(f)
    if new:
        w.writerow(["review_id", "product_id", "brand_id", "submission_time", "last_moderated", "rating", "is_syndicated",
                    "source_client", "incentivized", "campaign_id", "ratings_only", "recommended", "pos", "owned_for"])
    df = open(dpath, "a", encoding="utf-8")

    def one(p):
        rows, off = [], 0
        while True:
            r = get(s, "dsg", "reviews", [("Filter", f"ProductId:eq:{p['product_id']}"),
                                          ("Filter", f"SubmissionTime:gte:{SINCE_EPOCH}"),
                                          ("Filter", "IsSyndicated:eq:false"),
                                          ("Sort", "SubmissionTime:desc"), ("Limit", "100"), ("Offset", str(off))])
            res = r.get("Results", [])
            for x in res:
                b = x.get("Badges") or {}
                c = x.get("ContextDataValues") or {}
                inc = ("incentivizedReview" in b) or (str((c.get("IncentivizedReview") or {}).get("Value", "")).lower() == "true")
                rows.append([x.get("Id"), p["product_id"], p["brand_id"], x.get("SubmissionTime"), x.get("LastModeratedTime"),
                             x.get("Rating"), x.get("IsSyndicated"), x.get("SourceClient"), int(inc), x.get("CampaignId"),
                             x.get("IsRatingsOnly"), x.get("IsRecommended"), (c.get("POS") or {}).get("Value"),
                             (c.get("OwnedFor") or {}).get("Value")])
            tot = r.get("TotalResults")
            off += 100
            if tot is None or off >= tot or not res:
                break
        return p["product_id"], rows, tot is not None

    n = 0
    with ThreadPoolExecutor(6) as ex:
        futs = [ex.submit(one, p) for p in prods]
        for fu in as_completed(futs):
            pid, rows, ok = fu.result()
            with lock:
                w.writerows(rows)
                if ok:
                    df.write(pid + "\n")
                n += 1
                if n % 500 == 0:
                    f.flush(); df.flush(); print("done", n, flush=True)
    f.close(); df.close()


if __name__ == "__main__":
    step = sys.argv[1]
    extra = sys.argv[2:]
    if step == "products":
        products(extra or BRANDS)
    elif step == "reviews":
        reviews(set(extra) if extra else None)
