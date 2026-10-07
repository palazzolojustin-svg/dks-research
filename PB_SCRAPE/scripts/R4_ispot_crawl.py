"""R4: iSpot.tv public TV-spot census for DICK'S Sporting Goods and its owned brands.

iSpot.tv public pages (no login) show for each national TV spot: title, brand, description and
"Published <date>" (date iSpot first catalogued the spot), plus a public "N commercial airings" count
in link titles on brand/related lists. Metrics (spend, impressions, first/last airing) are locked.

Method: breadth-first crawl starting at the DKS and owned-brand iSpot brand pages; follow every
/ad/ link whose slug starts with a DKS-family prefix; parse each ad page.
Output: PB_SCRAPE\\raw\\R4_ispot_spots.csv (one row per spot) and R4_ispot_linktitles.csv.

Rerun weekly/monthly:  python PB_SCRAPE\\scripts\\R4_ispot_crawl.py
(then python PB_SCRAPE\\scripts\\R4_ispot_analyze.py). Polite 1 req/sec.
"""
import csv, re, time, html, pathlib, sys, requests
from collections import deque

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "raw"
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36",
     "Accept-Language": "en-US,en;q=0.9"}
PREFIXES = ("dicks-sporting-goods", "dicks-", "calia", "dsg", "vrst", "maxfli", "golf-galaxy", "walter-hagen", "public-lands",
            "alpine-design", "top-flite", "tommy-armour", "nishiki", "ethos", "fitness-gear", "house-of-sport", "gamechanger",
            "going-going-gone", "field-stream", "field-and-stream")
SEEDS = ["/brands/79N/dicks-sporting-goods", "/brands/nkO/calia", "/brands/5S8/vrst", "/brands/IBQ/maxfli", "/brands/IGj/golf-galaxy"]
SEEDS_FILE = pathlib.Path(__file__).with_name("R4_ispot_seeds.txt")  # extra /ad/ paths found via web search, one per line
if SEEDS_FILE.exists():
    SEEDS += [l.strip() for l in SEEDS_FILE.read_text().splitlines() if l.strip().startswith("/")]
SEEDS += sys.argv[1:]
SEEDS = list(dict.fromkeys(SEEDS))


def rel(slug):
    return slug.startswith(PREFIXES)


def main(max_pages=1500):
    s = requests.Session(); s.headers.update(H)
    q = deque(SEEDS); seen = set(SEEDS); rows = []; linkt = {}
    brands_seen = set(); brandstats = []
    n = 0
    while q and n < max_pages:
        path = q.popleft(); n += 1
        try:
            r = s.get("https://www.ispot.tv" + path, timeout=40)
        except Exception as e:
            print("ERR", path, e); time.sleep(5); continue
        t = r.text
        for a, ti in re.findall(r'href="(/ad/[A-Za-z0-9]{4}/[^"]+)"\s+title="([^"]*)"', t):
            slug = a.split("/")[3]
            if rel(slug):
                m = re.search(r"-\s*([\d,]+)\s+commercial airings", ti)
                if m:
                    linkt[a] = int(m.group(1).replace(",", ""))
                if a not in seen:
                    seen.add(a); q.append(a)
        for b in set(re.findall(r'href="(/brands/[A-Za-z0-9]{2,4}/[^"?#]+)"', t)):
            slug = b.split("/")[3]
            if rel(slug) and b not in seen:
                seen.add(b); q.append(b); brands_seen.add(b)
        if path.startswith("/brands/"):
            st = {k: v for k, v in re.findall(r'flex-grow-1">\s*([A-Za-z .]+?)\s*</div>\s*<div class="text-success overview-stat[^"]*">\s*([^<]+?)\s*</div>', t)}
            brandstats.append({"brand_path": path, **st}); print("BRAND", path, st, flush=True)
        if path.startswith("/ad/"):
            og = re.search(r'<meta property="og:title" content="([^"]*)"', t)
            desc = re.search(r'<meta property="og:description" content="([^"]*)"', t)
            pub = re.search(r"Published\s*</dt>\s*<dd[^>]*>\s*([A-Z][a-z]+ \d{1,2}, \d{4})", t)
            crumbs = re.findall(r'"name":\s*"([^"]+)",\s*"item":\s*"https://www.ispot.tv/(brands/[^"]+)"', t)
            tags = re.search(r'<meta property="og:video:tag" content="([^"]*)"', t)
            vis = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S))))
            pm = re.search(r"Advertiser Profiles [A-Za-z ,]{0,80}? Products (.{3,600}?) (?:Songs|Mood|Actors|Ad URL|Events|Contact Sales)", vis)
            um = re.search(r"Ad URL (\S+)", vis)
            rows.append({"path": path, "status": r.status_code,
                         "title": html.unescape(og.group(1)) if og else "",
                         "published": pub.group(1) if pub else "",
                         "brand": crumbs[-1][0] if crumbs else "", "brand_url": crumbs[-1][1] if crumbs else "",
                         "tags": html.unescape(tags.group(1)) if tags else "",
                         "products": pm.group(1) if pm else "", "ad_url": um.group(1) if um else "",
                         "description": html.unescape(html.unescape(desc.group(1))) if desc else ""})
        if n % 25 == 0:
            print(n, "pages; ads parsed", len(rows), "queue", len(q), flush=True)
        time.sleep(1.0)
    with open(RAW / "R4_ispot_spots.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["path", "status", "title", "published", "brand", "brand_url", "tags", "products", "ad_url", "description"])
        w.writeheader(); w.writerows(rows)
    with open(RAW / "R4_ispot_linktitles.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["path", "public_airings_count"])
        for k, v in linkt.items():
            w.writerow([k, v])
    import json; open(RAW / "R4_ispot_brandstats.json", "w").write(json.dumps(brandstats, indent=1))
    print("done", len(rows), "spots;", len(brands_seen), "brand pages:", sorted(brands_seen))


if __name__ == "__main__":
    main()




