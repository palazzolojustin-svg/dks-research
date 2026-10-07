"""G1: pull reviews (since 2023-01-01) for products listed in raw/G1_products_upc_<client>.jsonl for the given brands.
Same row format as R1_reviews_owned.csv (incl. POS / OwnedFor context values).
USAGE: python G1_bv_reviews_tail.py dsg DBX P-TEX Jawbone Slazenger DICK_S_Sporting_Goods Tour_Trek
OUT:   raw/G1_reviews_<client>_tail.csv  (resumable via raw/G1_reviews_<client>_tail_done.txt)
"""
import os, sys, json, csv, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, os.path.dirname(__file__))
from X01_bv_reviews import session_for, get, RAW, SINCE, SINCE_EPOCH

lock = threading.Lock()


def main(client, brands, tag="tail"):
    s = session_for(client)
    P = [json.loads(l) for l in open(os.path.join(RAW, f"G1_products_upc_{client}.jsonl"), encoding="utf-8")]
    P = [p for p in P if p["brand"] in brands and p["last_sub"] and p["last_sub"][:10] >= SINCE]
    out = os.path.join(RAW, f"G1_reviews_{client}_{tag}.csv")
    donef = os.path.join(RAW, f"G1_reviews_{client}_{tag}_done.txt")
    done = set(open(donef).read().split()) if os.path.exists(donef) else set()
    P = [p for p in P if p["id"] not in done]
    print("products", len(P), flush=True)
    new = not os.path.exists(out)
    f = open(out, "a", newline="", encoding="utf-8"); w = csv.writer(f)
    if new:
        w.writerow(["review_id", "product_id", "brand_id", "submission_time", "last_moderated", "rating", "is_syndicated",
                    "source_client", "incentivized", "campaign_id", "ratings_only", "recommended", "pos", "owned_for"])
    df = open(donef, "a")

    def one(p):
        rows, off, ok = [], 0, True
        while True:
            r = get(s, client, "reviews", [("Filter", f"ProductId:eq:{p['id']}"), ("Filter", f"SubmissionTime:gte:{SINCE_EPOCH}"),
                                         ("Sort", "SubmissionTime:desc"), ("Limit", "100"), ("Offset", str(off))])
            if r.get("TotalResults") is None:
                ok = False; break
            for x in r.get("Results", []):
                b = x.get("Badges") or {}; c = x.get("ContextDataValues") or {}
                inc = ("incentivizedReview" in b) or str((c.get("IncentivizedReview") or {}).get("Value", "")).lower() == "true"
                rows.append([x.get("Id"), p["id"], p["brand"], x.get("SubmissionTime"), x.get("LastModeratedTime"), x.get("Rating"),
                             x.get("IsSyndicated"), x.get("SourceClient"), int(inc), x.get("CampaignId"), x.get("IsRatingsOnly"),
                             x.get("IsRecommended"), (c.get("POS") or {}).get("Value"), (c.get("OwnedFor") or {}).get("Value")])
            off += 100
            if off >= r["TotalResults"] or not r.get("Results"):
                break
        return p["id"], rows, ok

    with ThreadPoolExecutor(6) as ex:
        for fu in as_completed([ex.submit(one, p) for p in P]):
            pid, rows, ok = fu.result()
            with lock:
                w.writerows(rows)
                if ok: df.write(pid + "\n")
    f.close(); df.close()


if __name__ == "__main__":
    client = sys.argv[1]
    brands = set(sys.argv[2:])
    main(client, brands)
