"""R7: Bazaarvoice catalog + review pull for the LICENSED (and tail exclusive) brands inside DKS "vertical brands".

WHY: DKS's 10-K "vertical brands" $ ($1.8B FY25, ~13% of DICK'S Business) includes brands DKS licenses
(adidas football, Cobra golf, Marucci baseball, Lotto soccer/pickleball; Prince until FY24). This script
enumerates those brands' products on dicks.com via the public Bazaarvoice front-door API (same access as
X01: header bv-bfd-token 13107,main_site,en_US, no login, no passkey) and pulls their reviews since 2023,
so licensed review volume can be compared with owned-brand review volume (X01_reviews_dsg.csv).

Brands are pulled whole (Lotto, Cobra, Marucci, Prince, Slazenger, Umbro, P-TEX, Jawbone, DBX, Tour_Trek,
PRIMED, Lady_Hagen) and adidas only inside sport categories where a licence is plausible (Football,
Baseball, Soccer, Tennis/Racquet).  Vendor code = characters 3-5 of the DKS style id (e.g. 26MCCU... -> MCC).

OUTPUT  raw/R7_products_licensed.csv, raw/R7_reviews_licensed.csv (+ _done.txt for resume)
RERUN   python R7_bv_licensed.py products ; python R7_bv_licensed.py reviews ; python R7_analyze.py
        Delete the two CSVs + _done.txt for a full refresh (~15 min, ~3-5k requests, 6 threads).
"""
import csv, os, sys, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, os.path.dirname(__file__))
from X01_bv_reviews import session_for, get, RAW

SINCE_EPOCH = 1672531200  # 2023-01-01
WHOLE = ["Lotto", "Cobra", "Marucci", "Prince", "Slazenger", "Umbro", "P-TEX", "Jawbone", "DBX", "Tour_Trek",
         "PRIMED", "Lady_Hagen"]
ADIDAS_CATS = ["Football-129207", "Baseball-128772", "Soccer-129627", "TennisRacquetSports-129679"]
PP = os.path.join(RAW, "R7_products_licensed.csv")
RP = os.path.join(RAW, "R7_reviews_licensed.csv")
DP = os.path.join(RAW, "R7_reviews_licensed_done.txt")
lock = threading.Lock()


def products():
    s = session_for("dsg")
    jobs = [(b, [("Filter", f"BrandId:eq:{b}")], b) for b in WHOLE]
    jobs += [("adidas", [("Filter", "BrandId:eq:adidas"), ("Filter", f"CategoryAncestorId:eq:{c}")], "adidas|" + c)
             for c in ADIDAS_CATS]
    seen = set()
    with open(PP, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["product_id", "vendor", "brand_id", "pull", "brand_name", "name", "category_id", "ancestry",
                    "active", "total_reviews", "avg_rating", "first_sub", "last_sub"])
        for b, flt, tag in jobs:
            n = get(s, "dsg", "products", flt + [("Limit", "1")]).get("TotalResults") or 0
            print(tag, n, flush=True)

            def page(o):
                return get(s, "dsg", "products", flt + [("Stats", "Reviews"), ("Limit", "100"), ("Offset", str(o))])
            with ThreadPoolExecutor(6) as ex:
                for r in ex.map(page, range(0, n, 100)):
                    for x in r.get("Results", []):
                        if x["Id"] in seen:
                            continue
                        seen.add(x["Id"])
                        st = x.get("ReviewStatistics") or {}
                        pid = x["Id"]
                        vend = pid[2:5] if pid[:2].isdigit() else pid[:6]
                        w.writerow([pid, vend, b, tag, (x.get("Brand") or {}).get("Name"), x.get("Name"),
                                    x.get("CategoryId"), "|".join(x.get("CategoryAncestryIds") or []), x.get("Active"),
                                    st.get("TotalReviewCount"), st.get("AverageOverallRating"),
                                    st.get("FirstSubmissionTime"), st.get("LastSubmissionTime")])


def reviews():
    s = session_for("dsg")
    with open(PP, encoding="utf-8") as f:
        prods = [r for r in csv.DictReader(f) if r["last_sub"] and r["last_sub"][:10] >= "2023-01-01"]
    done = set(open(DP, encoding="utf-8").read().split()) if os.path.exists(DP) else set()
    prods = [p for p in prods if p["product_id"] not in done]
    print("products to fetch", len(prods), flush=True)
    new = not os.path.exists(RP)
    f = open(RP, "a", newline="", encoding="utf-8"); w = csv.writer(f)
    if new:
        w.writerow(["review_id", "product_id", "brand_id", "vendor", "submission_time", "rating", "is_syndicated",
                    "source_client", "incentivized", "campaign_id", "ratings_only", "recommended"])
    dfile = open(DP, "a", encoding="utf-8")

    def one(p):
        rows, off = [], 0
        while True:
            r = get(s, "dsg", "reviews", [("Filter", f"ProductId:eq:{p['product_id']}"),
                                          ("Filter", f"SubmissionTime:gte:{SINCE_EPOCH}"),
                                          ("Sort", "SubmissionTime:desc"), ("Limit", "100"), ("Offset", str(off))])
            res = r.get("Results", [])
            for x in res:
                badges = x.get("Badges") or {}
                ctx = x.get("ContextDataValues") or {}
                inc = ("incentivizedReview" in badges) or (str((ctx.get("IncentivizedReview") or {}).get("Value", "")).lower() == "true")
                rows.append([x.get("Id"), p["product_id"], p["brand_id"], p["vendor"], x.get("SubmissionTime"),
                             x.get("Rating"), x.get("IsSyndicated"), x.get("SourceClient"), int(inc), x.get("CampaignId"),
                             x.get("IsRatingsOnly"), x.get("IsRecommended")])
            tot = r.get("TotalResults") or 0
            off += 100
            if off >= tot or not res or r.get("TotalResults") is None:
                break
        return p["product_id"], rows, r.get("TotalResults") is not None

    n = 0
    with ThreadPoolExecutor(6) as ex:
        for fu in as_completed([ex.submit(one, p) for p in prods]):
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
    {"products": products, "reviews": reviews}[sys.argv[1]]()
