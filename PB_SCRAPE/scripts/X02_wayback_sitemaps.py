"""X02: pull archived dicks.com product sitemaps from the Wayback Machine to build a time series of
owned-brand product-page counts (complete sets exist for 2024-05-15 and 2025-05-22; Nov-2023 near-complete).

Rerun: python PB_SCRAPE\\scripts\\X02_wayback_sitemaps.py
Output: PB_SCRAPE\\raw\\X02_wb_sitemap_<timestamp-set>.csv (url, slug, pid, year_prefix, snapshot)
Then:   python PB_SCRAPE\\scripts\\X02_analyze_sitemap.py <that csv>
To discover new snapshots: CDX query
  https://web.archive.org/cdx/search/cdx?url=dickssportinggoods.com/seo_sitemap_products&matchType=prefix&from=2023
"""
import re, csv, time, requests

RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\PB_SCRAPE\raw"
H = {"User-Agent": "Mozilla/5.0 research-script (X02)"}
SETS = {
    "2024-05": ["20240515192331/1", "20240515192353/2", "20240515192413/3", "20240515192432/4",
                "20240515192453/5", "20240515192514/6"],
    "2025-05": ["20250522221643/1", "20250522221720/2", "20250522221752/3", "20250522221834/4",
                "20250522221920/5", "20250522221956/6"],
    "2023-11": ["20231114171419/1", "20231110075248/2", "20231112135939/3", "20231110084949/4",
                "20230308151853/5", "20231111035445/6", "20231110084640/7"],
}


import os
CACHE = RAW + r"\X02_wb_cache"
os.makedirs(CACHE, exist_ok=True)


def fetch(ts, n):
    cp = f"{CACHE}\\{ts}_{n}.xml"
    if os.path.exists(cp) and os.path.getsize(cp) > 1000:
        return open(cp, encoding="utf-8").read()
    u = f"https://web.archive.org/web/{ts}id_/https://www.dickssportinggoods.com/seo_sitemap_products_{n}.xml"
    for i in range(8):
        try:
            r = requests.get(u, headers=H, timeout=180)
            if r.status_code == 200 and "<loc>" in r.text:
                open(cp, "w", encoding="utf-8").write(r.text)
                return r.text
            print(u, r.status_code)
        except Exception as e:
            print(u, str(e)[:80])
        time.sleep(30 * (i + 1))
    return ""


for name, parts in SETS.items():
    rows = []
    for p in parts:
        ts, n = p.split("/")
        txt = fetch(ts, n)
        locs = re.findall(r"<loc>(.*?)</loc>", txt)
        for loc in locs:
            mm = re.search(r"/p/([^/]+)/([^/?#]+)", loc)
            slug, pid = (mm.group(1), mm.group(2)) if mm else ("", "")
            pref = pid[:2] if pid[:2].isdigit() else ""
            rows.append([loc, slug, pid, pref, pid[2:5] if pref else "", "", ts])
        print(name, ts, n, len(locs))
        time.sleep(3)
    out = f"{RAW}\\X02_wb_sitemap_{name.replace('-', '')}.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["url", "slug", "pid", "year_prefix", "vendor_code", "lastmod", "sitemap"])
        w.writerows(rows)
    print("wrote", out, len(rows))
