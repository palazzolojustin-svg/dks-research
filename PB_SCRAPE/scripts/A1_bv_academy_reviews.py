"""A1 step 2: pull every native review since 2023-01-01 on Academy apparel products (any brand).

Input : raw/A1_academy_products_apparel.csv (from A1_bv_academy_catalog.py products)
Output: raw/A1_academy_reviews_apparel.csv  (review_id, product_id, submission_time, rating, campaign_id, syndicated,
        source_client, badges, ratings_only) ; resumable via raw/A1_academy_reviews_done.txt
Access: academy Bazaarvoice front door (single ProductId filter required by the syndication passkey).
RERUN (weekly): delete the two output files and rerun (~30-45 min at 8 threads), then python A1_analyze.py
"""
import csv, os, sys, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, os.path.dirname(__file__))
from A1_bv_academy_common import session, get, RAW

SINCE_EPOCH = 1672531200  # 2023-01-01
PP = os.path.join(RAW, "A1_academy_products_apparel.csv")
RP = os.path.join(RAW, "A1_academy_reviews_apparel.csv")
DP = os.path.join(RAW, "A1_academy_reviews_done.txt")
lock = threading.Lock()


def main():
    s = session()
    with open(PP, encoding="utf-8") as f:
        prods = [r for r in csv.DictReader(f) if (r["last_sub"] or "")[:10] >= "2023-01-01"]
    done = set(open(DP, encoding="utf-8").read().split()) if os.path.exists(DP) else set()
    prods = [p for p in prods if p["product_id"] not in done]
    print("products to fetch", len(prods), flush=True)
    new = not os.path.exists(RP)
    f = open(RP, "a", newline="", encoding="utf-8"); w = csv.writer(f)
    if new:
        w.writerow(["review_id", "product_id", "submission_time", "rating", "campaign_id", "syndicated", "source_client",
                    "badges", "ratings_only"])
    df = open(DP, "a", encoding="utf-8")

    def one(p):
        rows, off, ok = [], 0, True
        while True:
            r = get(s, "reviews", [("Filter", f"ProductId:eq:{p['product_id']}"), ("Filter", f"SubmissionTime:gte:{SINCE_EPOCH}"),
                                   ("Filter", "IsSyndicated:eq:false"), ("Sort", "SubmissionTime:desc"),
                                   ("Limit", "100"), ("Offset", str(off))])
            if r.get("TotalResults") is None:
                ok = False; break
            res = r.get("Results", [])
            for x in res:
                rows.append([x.get("Id"), p["product_id"], x.get("SubmissionTime"), x.get("Rating"), x.get("CampaignId"),
                             x.get("IsSyndicated"), x.get("SourceClient"), "|".join(sorted((x.get("Badges") or {}).keys())),
                             x.get("IsRatingsOnly")])
            off += 100
            if off >= r["TotalResults"] or not res:
                break
        return p["product_id"], rows, ok

    n = 0
    with ThreadPoolExecutor(8) as ex:
        futs = [ex.submit(one, p) for p in prods]
        for fu in as_completed(futs):
            pid, rows, ok = fu.result()
            with lock:
                w.writerows(rows)
                if ok:
                    df.write(pid + "\n")
                n += 1
                if n % 1000 == 0:
                    f.flush(); df.flush(); print("done", n, flush=True)
    f.close(); df.close()


if __name__ == "__main__":
    main()
