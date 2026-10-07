"""X01: DICK'S Sporting Goods / Golf Galaxy review-velocity scraper (Bazaarvoice front-door API).

WHY: dicks.com reviews are hosted by Bazaarvoice (client "dsg", displayCode 13107; Golf Galaxy client
"golfgalaxy", displayCode 15899). Bazaarvoice's public "front door" (BFD) endpoint serves the same
Conversations API that the product pages call, with no passkey and no Akamai wall:
  https://apps.bazaarvoice.com/bfd/v1/clients/<client>/api-products/cv2/resources/data/<products|reviews>.json
  header  bv-bfd-token: <displayCode>,main_site,en_US
Constraint: the dsg passkey has syndication on, so reviews.json must be filtered by a SINGLE ProductId
(or a single CategoryAncestorId / AuthorId). products.json accepts Filter=BrandId:eq:<BrandId>.

WHAT IT DOES
  step "products": for each brand in BRANDS, page through products.json (Stats=Reviews) and save
                   raw/X01_products_<client>.csv (Id, brand, name, category, active, total reviews, first/last submission).
  step "reviews":  for every product with LastSubmissionTime >= SINCE, page through reviews.json sorted by
                   SubmissionTime desc (Filter SubmissionTime>=SINCE) and save slim rows to
                   raw/X01_reviews_<client>.csv (product, brand, date, rating, syndicated, source client,
                   incentivized badge, campaign id, ratings-only).
  Resumable: products already present in the reviews CSV are skipped.

RERUN (weekly):  python X01_bv_reviews.py products dsg ; python X01_bv_reviews.py reviews dsg
                 (same with golfgalaxy). Then run X01_analyze.py.
Politeness: 6 worker threads, retries with backoff. Full owned-brand run ~ 10k requests.
"""
import csv, os, sys, time, json, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\PB_SCRAPE\raw"
CLIENTS = {"dsg": "13107", "golfgalaxy": "15899"}
REFERER = {"dsg": "https://www.dickssportinggoods.com/", "golfgalaxy": "https://www.golfgalaxy.com/"}
SINCE = "2023-01-01"
SINCE_EPOCH = 1672531200

OWNED = ["Calia", "CALIA_by_Carrie_Underwood", "VRST", "DSG", "Maxfli", "Walter_Hagen", "Lady_Hagen",
         "Alpine_Design", "ETHOS", "Fitness_Gear", "Top_Flite", "Tommy_Armour_Golf", "Nishiki", "Quest",
         "PRIMED", "Field___Stream"]
COMPARE = []  # national brands added via argv: python X01_bv_reviews.py products dsg Under_Armour Titleist
OWNED_SET = set(OWNED)

lock = threading.Lock()


def session_for(client):
    s = requests.Session()
    s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36",
                      "bv-bfd-token": f"{CLIENTS[client]},main_site,en_US",
                      "Origin": REFERER[client].rstrip("/"), "Referer": REFERER[client]})
    return s


def get(s, client, res, params, tries=5):
    url = f"https://apps.bazaarvoice.com/bfd/v1/clients/{client}/api-products/cv2/resources/data/{res}.json"
    params = list(params) + [("apiversion", "5.4")]
    for i in range(tries):
        try:
            r = s.get(url, params=params, timeout=90)
            if r.status_code == 200:
                j = r.json()
                return j.get("response", j)
            time.sleep(2 * (i + 1))
        except Exception:
            time.sleep(2 * (i + 1))
    return {"Results": [], "TotalResults": None, "Errors": ["failed"]}


def products(client, brands):
    s = session_for(client)
    path = os.path.join(RAW, f"X01_products_{client}.csv")
    have = set()
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            have = {r["brand_id"] for r in csv.DictReader(f)}
    new = not os.path.exists(path)
    f = open(path, "a", newline="", encoding="utf-8")
    w = csv.writer(f)
    if new:
        w.writerow(["product_id", "brand_id", "brand_name", "owned", "name", "category_id", "ancestry", "active",
                    "total_reviews", "avg_rating", "first_sub", "last_sub"])
    for b in brands:
        if b in have:
            print("skip", b); continue
        first = get(s, client, "products", [("Filter", f"BrandId:eq:{b}"), ("Limit", "1")])
        n = first.get("TotalResults") or 0
        print(client, b, n, flush=True)
        offs = list(range(0, n, 100))

        def page(o):
            return get(s, client, "products", [("Filter", f"BrandId:eq:{b}"), ("Stats", "Reviews"), ("Limit", "100"), ("Offset", str(o))])
        with ThreadPoolExecutor(6) as ex:
            for r in ex.map(page, offs):
                for x in r.get("Results", []):
                    st = x.get("ReviewStatistics") or {}
                    w.writerow([x["Id"], b, (x.get("Brand") or {}).get("Name"), int(b in OWNED_SET), x.get("Name"),
                                x.get("CategoryId"), "|".join(x.get("CategoryAncestryIds") or []), x.get("Active"),
                                st.get("TotalReviewCount"), st.get("AverageOverallRating"),
                                st.get("FirstSubmissionTime"), st.get("LastSubmissionTime")])
        f.flush()
    f.close()


def reviews(client, only_brands=None):
    s = session_for(client)
    ppath = os.path.join(RAW, f"X01_products_{client}.csv")
    rpath = os.path.join(RAW, f"X01_reviews_{client}.csv")
    donepath = os.path.join(RAW, f"X01_reviews_{client}_done.txt")
    with open(ppath, encoding="utf-8") as f:
        prods = [r for r in csv.DictReader(f)
                 if r["last_sub"] and r["last_sub"][:10] >= SINCE and (not only_brands or r["brand_id"] in only_brands)]
    done = set()
    if os.path.exists(donepath):
        done = set(open(donepath, encoding="utf-8").read().split())
    prods = [p for p in prods if p["product_id"] not in done]
    print(client, "products to fetch", len(prods), flush=True)
    new = not os.path.exists(rpath)
    f = open(rpath, "a", newline="", encoding="utf-8")
    w = csv.writer(f)
    if new:
        w.writerow(["review_id", "product_id", "brand_id", "owned", "submission_time", "rating", "is_syndicated",
                    "source_client", "incentivized", "campaign_id", "ratings_only", "recommended"])
    dfile = open(donepath, "a", encoding="utf-8")

    def one(p):
        rows, off = [], 0
        while True:
            r = get(s, client, "reviews", [("Filter", f"ProductId:eq:{p['product_id']}"),
                                         ("Filter", f"SubmissionTime:gte:{SINCE_EPOCH}"),
                                         ("Sort", "SubmissionTime:desc"), ("Limit", "100"), ("Offset", str(off))])
            res = r.get("Results", [])
            for x in res:
                badges = x.get("Badges") or {}
                ctx = x.get("ContextDataValues") or {}
                inc = ("incentivizedReview" in badges) or (str((ctx.get("IncentivizedReview") or {}).get("Value", "")).lower() == "true")
                rows.append([x.get("Id"), p["product_id"], p["brand_id"], p["owned"], x.get("SubmissionTime"), x.get("Rating"),
                             x.get("IsSyndicated"), x.get("SourceClient"), int(inc), x.get("CampaignId"),
                             x.get("IsRatingsOnly"), x.get("IsRecommended")])
            tot = r.get("TotalResults") or 0
            off += 100
            if off >= tot or not res or r.get("TotalResults") is None:
                break
        return p["product_id"], rows, r.get("TotalResults") is not None

    n = 0
    with ThreadPoolExecutor(6) as ex:
        futs = [ex.submit(one, p) for p in prods]
        for fu in as_completed(futs):
            pid, rows, ok = fu.result()
            with lock:
                w.writerows(rows)
                if ok:
                    dfile.write(pid + "\n")
                n += 1
                if n % 200 == 0:
                    f.flush(); dfile.flush(); print("done", n, flush=True)
    f.close(); dfile.close()


if __name__ == "__main__":
    step, client = sys.argv[1], sys.argv[2]
    extra = sys.argv[3:]
    if step == "products":
        products(client, extra or OWNED)
    elif step == "reviews":
        reviews(client, set(extra) if extra else None)
