"""W08: YouTube search results (no API key) -> CSV of videos: query,videoId,title,channel,views,published_rel.
Usage: python3 -I W08_youtube_search.py <out_csv> "q1" "q2" ...
Uses sp=CAI%3D (sort by upload date) and also relevance; follows continuation pages up to N.
"""
import sys, re, json, time, csv
import requests

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
S = requests.Session()
S.headers.update({"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
S.cookies.set("CONSENT", "YES+1", domain=".youtube.com")


def walk(o, out):
    if isinstance(o, dict):
        if "videoRenderer" in o:
            out.append(o["videoRenderer"])
        for v in o.values():
            walk(v, out)
    elif isinstance(o, list):
        for v in o:
            walk(v, out)


def find_cont(o):
    if isinstance(o, dict):
        if "continuationCommand" in o:
            return o["continuationCommand"]["token"]
        for v in o.values():
            t = find_cont(v)
            if t:
                return t
    elif isinstance(o, list):
        for v in o:
            t = find_cont(v)
            if t:
                return t
    return None


def txt(x):
    if not x:
        return ""
    if "simpleText" in x:
        return x["simpleText"]
    return "".join(r.get("text", "") for r in x.get("runs", []))


def search(q, sp, pages=4):
    r = S.get("https://www.youtube.com/results", params={"search_query": q, "sp": sp} if sp else {"search_query": q}, timeout=30)
    m = re.search(r"var ytInitialData = (\{.*?\});</script>", r.text)
    key = re.search(r'"INNERTUBE_API_KEY":"([^"]+)"', r.text)
    ver = re.search(r'"INNERTUBE_CLIENT_VERSION":"([^"]+)"', r.text)
    data = json.loads(m.group(1))
    vids = []
    walk(data, vids)
    tok = find_cont(data)
    for _ in range(pages - 1):
        if not tok or not key:
            break
        time.sleep(1)
        body = {"context": {"client": {"clientName": "WEB", "clientVersion": ver.group(1), "hl": "en", "gl": "US"}}, "continuation": tok}
        j = S.post("https://www.youtube.com/youtubei/v1/search?key=" + key.group(1), json=body, timeout=30).json()
        walk(j, vids)
        tok = find_cont(j)
    return vids


out = sys.argv[1]
rows = []
seen = set()
for q in sys.argv[2:]:
    for sp in ("CAI%3D", None):
        try:
            vids = search(q, sp)
        except Exception as e:
            print("ERR", q, e)
            continue
        for v in vids:
            vid = v.get("videoId")
            key = (q, vid)
            if key in seen:
                continue
            seen.add(key)
            rows.append({"query": q, "sort": "date" if sp else "relevance", "videoId": vid, "title": txt(v.get("title")),
                         "channel": txt(v.get("ownerText")), "views": txt(v.get("viewCountText")),
                         "published": txt(v.get("publishedTimeText")), "length": txt(v.get("lengthText"))})
        print(q, sp, len(vids), flush=True)
        time.sleep(1.5)
with open(out, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print("rows", len(rows))
