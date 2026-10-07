"""X08 Reddit POST + COMMENT mentions of DKS owned apparel brands in targeted subreddits via Arctic Shift
(free, no key). Full-text search requires a subreddit; big subs (r/lululemon, r/femalefashionadvice) often
time out, so the script retries with backoff and records which (sub, term, kind) completed.

Rerun: python X08_arctic_brand_posts.py [start=2024-01-01] [end=2026-10-08]
Output: PB_SCRAPE/raw/X08_arctic_brand_hits.jsonl, X08_arctic_brand_status.csv, X08_arctic_brand_monthly.csv
Weekly use: rerun with start = last run date; compare trailing 6 months vs same months prior year.
"""
import requests, json, time, sys, os, csv, collections, datetime as dt

B = "https://arctic-shift.photon-reddit.com/api/"
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "raw")
start = sys.argv[1] if len(sys.argv) > 1 else "2024-01-01"
end = sys.argv[2] if len(sys.argv) > 2 else dt.date.today().isoformat()
PLAN = {
    "vrst": ["frugalmalefashion", "malefashionadvice", "lululemen", "golf", "mensfashion", "runningfashion", "DicksSportingGoods", "BuyItForLife", "activewear"],
    "calia": ["womengolf", "xxrunning", "yoga", "activewear", "orangetheory", "xxfitness", "DicksSportingGoods", "athleta_gap", "lululemon", "femalefashionadvice", "BuyItForLife", "Frugalfemalefashion"],
    "vuori": ["frugalmalefashion", "malefashionadvice", "lululemen", "golf", "mensfashion", "runningfashion", "activewear", "BuyItForLife"],
}


def get(ep, p):
    for i in range(6):
        try:
            r = requests.get(B + ep, params=p, timeout=120)
            j = r.json()
            if j.get("data") is not None:
                return j["data"]
        except Exception:
            pass
        time.sleep(8 * (i + 1))
    return None


hits = open(os.path.join(RAW, "X08_arctic_brand_hits.jsonl"), "a", encoding="utf-8")
stat = open(os.path.join(RAW, "X08_arctic_brand_status.csv"), "a", encoding="utf-8")
for term, subs in PLAN.items():
    for sub in subs:
        for kind, ep, key in [("post", "posts/search", "query"), ("comment", "comments/search", "body")]:
            after, n, ok = start, 0, True
            while True:
                d = get(ep, {"subreddit": sub, key: term, "after": after, "before": end, "limit": 100, "sort": "asc"})
                if d is None:
                    ok = False; break
                for x in d:
                    text = (x.get("title", "") + " || " + x.get("selftext", "")) if kind == "post" else x.get("body", "")
                    hits.write(json.dumps({"term": term, "sub": sub, "kind": kind, "id": x["id"], "t": int(x["created_utc"]),
                                           "text": text[:600]}) + "\n")
                n += len(d)
                if len(d) < 100:
                    break
                after = int(d[-1]["created_utc"]) + 1
                time.sleep(2)
            stat.write(f"{term},{sub},{kind},{n},{'ok' if ok else 'failed'},{dt.datetime.now().isoformat()}\n")
            stat.flush(); hits.flush()
            print(term, sub, kind, n, ok, flush=True)
            time.sleep(3)
hits.close(); stat.close()

# monthly summary
seen, agg = set(), collections.defaultdict(collections.Counter)
for line in open(os.path.join(RAW, "X08_arctic_brand_hits.jsonl"), encoding="utf-8"):
    x = json.loads(line)
    k = (x["kind"], x["id"], x["term"])
    if k in seen:
        continue
    seen.add(k)
    m = dt.datetime.fromtimestamp(x["t"], dt.timezone.utc).strftime("%Y-%m")
    agg[m][x["term"]] += 1
with open(os.path.join(RAW, "X08_arctic_brand_monthly.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["month"] + list(PLAN))
    for m in sorted(agg):
        w.writerow([m] + [agg[m][t] for t in PLAN]); print(m, *[agg[m][t] for t in PLAN])
