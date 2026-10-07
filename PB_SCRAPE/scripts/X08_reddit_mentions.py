"""X08 Reddit mention collector (PullPush API, free, no login, no key).

Pulls every Reddit submission + comment matching each query per calendar month (Jan-2024 .. now)
from the public PullPush search API (https://api.pullpush.io/reddit/search/{submission|comment}/),
paging backwards 100 at a time. Saves ALL raw hits (deduped by id) so that brand-context filtering
is done afterwards in X08_reddit_analyze.py (no re-fetch needed when filters change).

Rerun weekly (incremental, e.g. just the latest month):
    python X08_reddit_mentions.py --start 2026-10 --end 2026-10
Output: PB_SCRAPE/raw/X08_reddit_raw.jsonl   (one JSON per hit: q, kind, id, t, sub, author, score, text)
Notes: PullPush 'q' is AND-of-words, case-insensitive; phrase quotes return nothing.
       PullPush is flaky (SSL EOF / 5xx) -> retries with backoff. Coverage gaps are possible, so always
       normalise owned-brand counts by benchmark brands (vuori, athleta) collected the same way.
"""
import requests, time, json, sys, os, datetime as dt, argparse

H = {"User-Agent": "dks-research-script/0.1"}
BASE = "https://api.pullpush.io/reddit/search/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "raw", "X08_reddit_raw.jsonl")

QUERIES = ["calia", "vrst", "maxfli", "vuori", "athleta",
           "dsg leggings", "dsg joggers", "dsg shorts", "dsg shirt", "dsg brand", "dsg jacket",
           "dsg hoodie", "dsg pants", "dsg bra", "dsg dicks"]


def ts(y, m):
    return int(dt.datetime(y, m, 1, tzinfo=dt.timezone.utc).timestamp())


def get(kind, p):
    for attempt in range(5):
        try:
            r = requests.get(BASE + kind + "/", params=p, headers=H, timeout=90)
            if r.status_code == 200:
                return r.json().get("data") or []
        except Exception:
            pass
        time.sleep(3 * (attempt + 1))
    return None


def fetch(kind, q, after, before, cap):
    out, b = [], before
    while True:
        d = get(kind, {"q": q, "after": after, "before": b, "size": 100, "sort": "desc", "sort_type": "created_utc"})
        if d is None:
            print("FAILED", kind, q, after, b, file=sys.stderr, flush=True)
            return out, "failed"
        if not d:
            return out, "complete"
        out.extend(d)
        newb = min(int(x["created_utc"]) for x in d)
        if len(d) < 100:
            return out, "complete"
        if newb >= b or len(out) >= cap:
            return out, "capped"
        b = newb
        time.sleep(0.8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2024-01")
    ap.add_argument("--end", default=dt.date.today().strftime("%Y-%m"))
    ap.add_argument("--queries", default=",".join(QUERIES))
    ap.add_argument("--cap", type=int, default=5000)
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    global OUT
    if a.tag:
        OUT = OUT.replace("_raw.jsonl", "_raw_" + a.tag + ".jsonl")
    y, m = map(int, a.start.split("-"))
    ey, em = map(int, a.end.split("-"))
    f = open(OUT, "a", encoding="utf-8")
    log = open(OUT.replace("_raw", "_fetchlog").replace(".jsonl", ".csv"), "a", encoding="utf-8")
    while (y, m) <= (ey, em):
        ny, nm = (y + 1, 1) if m == 12 else (y, m + 1)
        after, before = ts(y, m), min(ts(ny, nm), int(time.time()))
        for q in a.queries.split(","):
            for kind in ("submission", "comment"):
                data, status = fetch(kind, q, after, before, a.cap)
                seen = set()
                for x in data:
                    if x.get("id") in seen:
                        continue
                    seen.add(x.get("id"))
                    text = (x.get("title", "") + " || " + x.get("selftext", "")) if kind == "submission" else x.get("body", "")
                    f.write(json.dumps({"q": q, "kind": kind, "id": x.get("id"), "t": int(x["created_utc"]),
                                        "sub": x.get("subreddit"), "author": x.get("author"), "score": x.get("score"),
                                        "text": text[:1500]}) + "\n")
                log.write(f"{y}-{m:02d},{q},{kind},{len(seen)},{status},{dt.datetime.now().isoformat()}\n")
                log.flush(); f.flush()
                print(f"{y}-{m:02d} {q} {kind} {len(seen)} {status}", flush=True)
        y, m = ny, nm
    f.close(); log.close()


if __name__ == "__main__":
    main()


