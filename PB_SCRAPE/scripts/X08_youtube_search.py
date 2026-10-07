"""X08 YouTube video census for DKS owned apparel brands (no API key; uses the same public
youtubei/v1/search endpoint the youtube.com results page calls).

For each query, pulls results sorted by upload date (sp=CAI%3D) with continuation paging, records
videoId, title, channel, publishedTimeText ("3 months ago"), views. Relative ages are converted to an
approximate upload month (accurate to ~1 month for <1 year; to ~1 year beyond).
Rerun:  python X08_youtube_search.py      -> PB_SCRAPE/raw/X08_youtube_videos.csv (appends with run date)
"""
import requests, re, json, csv, os, time, datetime as dt

H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36",
     "Accept-Language": "en-US,en;q=0.9"}
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "raw", "X08_youtube_videos.csv")
QUERIES = ["calia leggings", "calia haul", "calia review", "vrst review", "vrst haul", "vrst dicks",
           "dsg leggings", "dsg haul", "dicks sporting goods haul", "dsg joggers", "dicks brand leggings",
           "vuori review", "athleta haul"]


def get(url, **kw):
    for i in range(6):
        try:
            return requests.request(url=url, timeout=40, **kw)
        except Exception:
            time.sleep(3 * (i + 1))
    return None


def walk(o, key):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == key:
                yield v
            yield from walk(v, key)
    elif isinstance(o, list):
        for v in o:
            yield from walk(v, key)


def txt(x):
    if not x:
        return ""
    if "simpleText" in x:
        return x["simpleText"]
    return "".join(r.get("text", "") for r in x.get("runs", []))


def approx_month(rel, today):
    m = re.match(r"(?:Streamed )?(\d+) (second|minute|hour|day|week|month|year)s? ago", rel or "")
    if not m:
        return ""
    n, u = int(m.group(1)), m.group(2)
    days = {"second": 0, "minute": 0, "hour": 0, "day": 1, "week": 7, "month": 30.4, "year": 365}[u] * n
    return (today - dt.timedelta(days=days)).strftime("%Y-%m")


def run(q, today, max_pages=8):
    r = get("https://www.youtube.com/results", method="GET", params={"search_query": q, "sp": "CAI%3D"}, headers=H)
    if r is None:
        return []
    t = r.text
    key = re.search(r'"INNERTUBE_API_KEY":"([^"]+)"', t)
    ver = re.search(r'"INNERTUBE_CLIENT_VERSION":"([^"]+)"', t)
    m = re.search(r"var ytInitialData = (\{.*?\});</script>", t)
    if not m:
        return []
    data = json.loads(m.group(1))
    rows, pages = [], 0
    while True:
        for v in walk(data, "videoRenderer"):
            rows.append({"query": q, "videoId": v.get("videoId"), "title": txt(v.get("title")),
                         "channel": txt(v.get("ownerText")), "published": txt(v.get("publishedTimeText")),
                         "views": txt(v.get("viewCountText")),
                         "approx_month": approx_month(txt(v.get("publishedTimeText")), today)})
        tok = [c for c in walk(data, "continuationCommand")]
        pages += 1
        if not tok or pages >= max_pages or not key:
            break
        body = {"context": {"client": {"clientName": "WEB", "clientVersion": ver.group(1), "hl": "en", "gl": "US"}},
                "continuation": tok[-1]["token"]}
        rr = get("https://www.youtube.com/youtubei/v1/search?key=" + key.group(1), method="POST", json=body, headers=H)
        if rr is None or rr.status_code != 200:
            break
        data = rr.json()
        time.sleep(1)
    return rows


def main():
    today = dt.date.today()
    allrows = []
    for q in QUERIES:
        rows = run(q, today)
        print(q, len(rows), flush=True)
        allrows += rows
        time.sleep(2)
    new = not os.path.exists(OUT)
    with open(OUT, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["run_date", "query", "videoId", "title", "channel", "published", "views", "approx_month"])
        if new:
            w.writeheader()
        for r in allrows:
            r["run_date"] = today.isoformat()
            w.writerow(r)


if __name__ == "__main__":
    main()
