"""X07: monthly Reddit POST mention counts for DKS golf owned brands vs benchmark golf-ball brands.

Source: Arctic Shift public Reddit archive API (https://arctic-shift.photon-reddit.com), no auth.
  - /api/posts/search?subreddit=..&query=..&after=..&before=..&limit=100&sort=asc  (full-text title+selftext)
    paginated over the whole window per (subreddit, term), then binned by month locally (few requests).
  - /api/posts/search/aggregate?aggregate=created_utc&frequency=month&subreddit=..  (total posts, for normalisation)
Rerun:  python X07_reddit_golf_mentions.py [start=2023-01-01] [end=2026-10-07]
Outputs (PB_SCRAPE\\raw):
  X07_reddit_posts_<sub>_<term>.json   raw id/created_utc/title/score/num_comments per matching post
  X07_reddit_golf_mentions.csv          subreddit, term, month, posts
  X07_reddit_golf_totals.csv            subreddit, month, total_posts
Weekly use: rerun; compare trailing-6-month sum vs same months prior year, and Maxfli share of mentions vs Pro V1/Kirkland/Vice.
Caveats: archive ingestion can lag or miss posts; the current month is partial; full-text matches include off-topic mentions.
"""
import csv
import json
import os
import sys
import time
from collections import Counter
from datetime import datetime, timezone

import requests

BASE = "https://arctic-shift.photon-reddit.com/api"
SUBS = ["golf", "GolfEquipment"]
TERMS = ["maxfli", "kirkland", "vice", "top flite", "pro v1"]
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "raw")


def get(url, params, tries=8):
    for i in range(tries):
        try:
            r = requests.get(url, params=params, timeout=90)
            if r.status_code == 200:
                j = r.json()
                if j.get("data") is not None:
                    return j["data"]
        except Exception:
            pass
        time.sleep(min(30, 3 * (i + 1)))
    return None


def to_epoch(d):
    return int(datetime.strptime(d, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp())


def month_windows(start, end):
    y, m = int(start[:4]), int(start[5:7])
    stop = to_epoch(end)
    while True:
        a = to_epoch(f"{y:04d}-{m:02d}-01")
        y2, m2 = (y + 1, 1) if m == 12 else (y, m + 1)
        b = min(to_epoch(f"{y2:04d}-{m2:02d}-01"), stop)
        if a >= stop:
            return
        yield a, b
        y, m = y2, m2


def pull(sub, term, start, end):
    """Monthly windows (the archive times out on long full-text windows)."""
    fn = os.path.join(RAW, f"X07_reddit_posts_{sub}_{term.replace(' ', '_')}.json")
    rows = []
    for a, b in month_windows(start, end):
        got = pull_window(sub, term, a, b)
        if got is None:
            print("FAILED", sub, term, datetime.fromtimestamp(a, timezone.utc).date(), flush=True)
            rows.append({"id": None, "created_utc": a, "failed": True})
        else:
            rows += got
        time.sleep(1)
    with open(fn, "w", encoding="utf8") as f:
        json.dump(rows, f)
    return rows


def pull_window(sub, term, cur, stop):
    rows = []
    while True:
        d = get(f"{BASE}/posts/search", {"subreddit": sub, "query": term, "after": cur, "before": stop, "limit": 100, "sort": "asc",
                                         "fields": "id,created_utc,title,score,num_comments"})
        if d is None:
            return None
        rows += d
        if len(d) < 100:
            return rows
        cur = int(d[-1]["created_utc"]) + 1
        time.sleep(0.5)


def main():
    start = sys.argv[1] if len(sys.argv) > 1 else "2023-01-01"
    end = sys.argv[2] if len(sys.argv) > 2 else "2026-10-07"
    out = os.path.join(RAW, "X07_reddit_golf_mentions.csv")
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["subreddit", "term", "month", "posts"])
        for term in TERMS:
            for sub in SUBS:
                rows = pull(sub, term, start, end)
                failed = {datetime.fromtimestamp(int(r["created_utc"]), timezone.utc).strftime("%Y-%m") for r in rows if r.get("failed")}
                c = Counter(datetime.fromtimestamp(int(r["created_utc"]), timezone.utc).strftime("%Y-%m") for r in rows if not r.get("failed"))
                for mo in sorted(set(c) | failed):
                    w.writerow([sub, term, mo, "" if mo in failed else c[mo]])
                f.flush()
                print(sub, term, len(rows), flush=True)
    tot = os.path.join(RAW, "X07_reddit_golf_totals.csv")
    with open(tot, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["subreddit", "month", "total_posts"])
        for sub in SUBS:
            y = int(start[:4])
            # yearly chunks keep the aggregate query light
            while y <= int(end[:4]):
                a, b = f"{y}-01-01", min(f"{y + 1}-01-01", end)
                d = get(f"{BASE}/posts/search/aggregate", {"aggregate": "created_utc", "frequency": "month", "subreddit": sub, "after": a, "before": b})
                for x in d or []:
                    # bucket timestamps are month starts in UTC+1; shift by a day to label correctly
                    ts = datetime.strptime(x["created_utc"][:10], "%Y-%m-%d")
                    mo = (ts.replace(day=1) if ts.day == 1 else datetime(ts.year + (ts.month == 12), ts.month % 12 + 1, 1)).strftime("%Y-%m")
                    w.writerow([sub, mo, x["count"]])
                y += 1
                time.sleep(1)


if __name__ == "__main__":
    main()
