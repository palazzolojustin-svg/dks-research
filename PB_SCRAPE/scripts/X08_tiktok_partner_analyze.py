"""X08 TikTok paid-creator (#caliapartner / #vrstpartner / #dkspartner) analysis.

Input: an Apify dataset export (clockworks/tiktok-hashtag-scraper, hashtags vrstpartner, caliapartner,
dkspartner, resultsPerPage 200) saved as JSON ({"items":[...]} or a bare list) with fields
input, createTimeISO, playCount, diggCount, commentCount, shareCount, authorMeta.name, authorMeta.fans, text, webVideoUrl.
The scraper's hashtag search is fuzzy (returns other "Calia" businesses, generic "partner" posts), so each video
is classified as a genuine DKS-brand video only if its caption references the DKS brand
(CALIA: '@calia' / 'calia' + dick/dsg/activewear words; VRST: 'vrst'; DKS: 'dick').
Rerun: python X08_tiktok_partner_analyze.py <export.json>
Output: PB_SCRAPE/raw/X08_tiktok_partner_videos.csv and monthly summary printed + X08_tiktok_partner_monthly.csv
"""
import json, sys, re, csv, os, collections

src = sys.argv[1]
raw = json.load(open(src, encoding="utf-8"))
items = raw["items"] if isinstance(raw, dict) else raw
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "raw")


def g(x, k):
    if k in x:
        return x[k]
    a, b = k.split(".") if "." in k else (k, None)
    v = x.get(a)
    return v.get(b) if isinstance(v, dict) and b else v


def classify(tag, text):
    t = (text or "").lower()
    if tag == "caliapartner":
        if re.search(r"@calia\b|#calia\b|calia\s*(by|activewear|legging|bra|set|haul|golf|studio)|dick'?s|dsg|#caliapartner", t) and \
           not re.search(r"sofa|restaurant|body\s*and\s*home|music|hungary|divano|furniture", t):
            return "CALIA" if re.search(r"calia", t) else ""
    if tag == "vrstpartner":
        if re.search(r"vrst", t):
            return "VRST"
    if tag == "dkspartner":
        if re.search(r"dick'?s|dicks|dsg|#dkspartner", t):
            return "DKS"
    return ""


rows = []
for x in items:
    tag = g(x, "input")
    text = g(x, "text") or ""
    brand = classify(tag, text)
    rows.append({"tag": tag, "brand": brand, "date": (g(x, "createTimeISO") or "")[:10],
                 "month": (g(x, "createTimeISO") or "")[:7], "plays": g(x, "playCount") or 0,
                 "likes": g(x, "diggCount") or 0, "author": g(x, "authorMeta.name"), "fans": g(x, "authorMeta.fans"),
                 "url": g(x, "webVideoUrl"), "text": text[:200].replace("\n", " ")})

with open(os.path.join(OUT, "X08_tiktok_partner_videos.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)

agg = collections.defaultdict(lambda: [0, 0, set()])
for r in rows:
    if r["brand"]:
        a = agg[(r["brand"], r["month"])]
        a[0] += 1; a[1] += r["plays"]; a[2].add(r["author"])
with open(os.path.join(OUT, "X08_tiktok_partner_monthly.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["brand", "month", "videos", "plays", "unique_creators"])
    for (b, m), (n, p, au) in sorted(agg.items()):
        w.writerow([b, m, n, p, len(au)])
        print(b, m, n, p, len(au))
print("classified:", collections.Counter((r["tag"], bool(r["brand"])) for r in rows))
