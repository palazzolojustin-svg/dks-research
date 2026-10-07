"""X08 Instagram owned-channel cadence & engagement for CALIA (@caliafitness) and VRST (@vrst).

Input: export of Apify actor instagram-scraper/fast-instagram-post-scraper (postsPerProfile 650) with fields
user.username, date, like_count, comment_count, view_count, type, product_type, caption, coauthor_producers, mentions.
Computes by account x month: posts, median likes/post, mean likes, total likes, median reel views, % posts that are
collab (coauthor) posts, and keyword counts (new launches: denim, golf, swim, kids, footwear, etc).
Rerun:  python X08_instagram_posts_analyze.py <export.json>
Output: PB_SCRAPE/raw/X08_instagram_posts.csv, X08_instagram_monthly.csv; prints summary.
"""
import json, sys, csv, os, statistics as st, collections, re

raw = json.load(open(sys.argv[1], encoding="utf-8"))
items = raw["items"] if isinstance(raw, dict) else raw
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "raw")


def g(x, k):
    if k in x:
        return x[k]
    a, b = k.split(".", 1)
    v = x.get(a)
    if isinstance(v, dict):
        return v.get(b)
    if isinstance(v, list):
        return [i.get(b) for i in v if isinstance(i, dict)]
    return None


rows = []
for x in items:
    d = str(g(x, "date") or "")
    rows.append({"acct": g(x, "user.username"), "date": d[:10], "month": d[:7],
                 "likes": g(x, "like_count") or 0, "comments": g(x, "comment_count") or 0,
                 "views": g(x, "view_count") or 0, "ptype": g(x, "product_type"),
                 "collab": 1 if g(x, "coauthor_producers.username") else 0,
                 "coauthors": "|".join(g(x, "coauthor_producers.username") or []),
                 "caption": (g(x, "caption") or "")[:300].replace("\n", " ")})
with open(os.path.join(OUT, "X08_instagram_posts.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

agg = collections.defaultdict(list)
for r in rows:
    agg[(r["acct"], r["month"])].append(r)
with open(os.path.join(OUT, "X08_instagram_monthly.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["acct", "month", "posts", "median_likes", "mean_likes", "total_likes", "median_comments", "median_reel_views", "collab_share"])
    for (a, m), rs in sorted(agg.items()):
        lk = [r["likes"] for r in rs]
        vw = [r["views"] for r in rs if r["views"]]
        line = [a, m, len(rs), st.median(lk), round(st.mean(lk)), sum(lk), st.median([r["comments"] for r in rs]),
                st.median(vw) if vw else "", round(sum(r["collab"] for r in rs) / len(rs), 2)]
        w.writerow(line); print(*line)

# half-year comparisons
def window(a, lo, hi):
    rs = [r for r in rows if r["acct"] == a and lo <= r["month"] <= hi]
    if not rs:
        return None
    vw = [r["views"] for r in rs if r["views"]]
    return dict(posts=len(rs), med_likes=st.median([r["likes"] for r in rs]), tot_likes=sum(r["likes"] for r in rs),
                med_views=st.median(vw) if vw else None, tot_views=sum(vw), collab=round(sum(r["collab"] for r in rs) / len(rs), 2))
for a in sorted(set(r["acct"] for r in rows)):
    for lo, hi in [("2024-04", "2024-09"), ("2025-04", "2025-09"), ("2026-04", "2026-09")]:
        print("WINDOW", a, lo, hi, window(a, lo, hi))
kw = ["denim", "golf", "swim", "kids", "girls", "boys", "footwear", "shoe", "sneaker", "pickleball", "tennis", "run", "pop-up|popup|hamptons", "new arrival|just dropped|new collection|launch"]
for a in sorted(set(r["acct"] for r in rows)):
    for yr in ["2024", "2025", "2026"]:
        rs = [r for r in rows if r["acct"] == a and r["month"].startswith(yr) and r["month"][5:] <= "09"]
        print("KW", a, yr + " Jan-Sep", len(rs), {k: sum(1 for r in rs if re.search(k, r["caption"], re.I)) for k in kw})
