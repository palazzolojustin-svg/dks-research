"""X07: retry/gap-fill for Reddit monthly mention counts, using WEEKLY sub-windows (lighter archive queries).

Rerun: python X07_reddit_retry.py <subreddit> <term> <YYYY-MM>[,<YYYY-MM>...]
Appends rows (subreddit, term, month, posts, n_weeks_failed) to PB_SCRAPE\\raw\\X07_reddit_retry.csv.
A month is complete only if n_weeks_failed == 0.
"""
import csv
import os
import sys
import time
from datetime import datetime, timedelta, timezone

import requests

B = "https://arctic-shift.photon-reddit.com/api/posts/search"
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "raw")


def q(sub, term, a, b):
    rows, cur = 0, a
    while True:
        d = None
        for i in range(6):
            try:
                r = requests.get(B, params={"subreddit": sub, "query": term, "after": cur, "before": b, "limit": 100, "sort": "asc",
                                            "fields": "id,created_utc"}, timeout=90)
                d = r.json().get("data")
                if d is not None:
                    break
            except Exception:
                pass
            time.sleep(min(30, 4 * (i + 1)))
        if d is None:
            return None
        rows += len(d)
        if len(d) < 100:
            return rows
        cur = int(d[-1]["created_utc"]) + 1


sub, term, months = sys.argv[1], sys.argv[2], sys.argv[3].split(",")
out = os.path.join(RAW, "X07_reddit_retry.csv")
new = not os.path.exists(out)
with open(out, "a", newline="") as f:
    w = csv.writer(f)
    if new:
        w.writerow(["subreddit", "term", "month", "posts", "n_weeks_failed"])
    for mo in months:
        y, m = int(mo[:4]), int(mo[5:7])
        start = datetime(y, m, 1, tzinfo=timezone.utc)
        end = datetime(y + (m == 12), m % 12 + 1, 1, tzinfo=timezone.utc)
        tot, fails, a = 0, 0, start
        while a < end:
            b = min(a + timedelta(days=7), end)
            n = q(sub, term, int(a.timestamp()), int(b.timestamp()))
            if n is None:
                fails += 1
            else:
                tot += n
            a = b
            time.sleep(1)
        w.writerow([sub, term, mo, tot, fails])
        f.flush()
        print(sub, term, mo, tot, fails, flush=True)
