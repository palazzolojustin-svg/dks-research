"""X02 sitemap census of dicks.com / golfgalaxy.com product URLs.

Rerun:  python PB_SCRAPE\\scripts\\X02_sitemap_census.py [site]
   site = dsg (default) | gg
What it does:
  1. Downloads the robots.txt-declared sitemap index (seo_sitemap.xml) and every seo_sitemap_products_N.xml.
  2. Saves every product URL to PB_SCRAPE\\raw\\X02_<site>_sitemap_urls_<YYYYMMDD>.csv with:
     slug, product id, 2-digit id prefix (DKS item ids start with a 2-digit year code, e.g. 26nik... = created for 2026),
     3-letter vendor code (chars 3-5 of id, e.g. 'nik', 'dks'), and lastmod if present.
  3. Owned-brand tagging is done in X02_analyze.py.
Weekly use: run it, then run X02_analyze.py; diff counts vs prior dated CSV.
"""
import re, sys, csv, time, datetime, requests

SITES = {"dsg": "https://www.dickssportinggoods.com", "gg": "https://www.golfgalaxy.com"}
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36"}
RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\PB_SCRAPE\raw"


def get(url):
    for i in range(3):
        try:
            r = requests.get(url, headers=H, timeout=120)
            if r.status_code == 200:
                return r.text
            print(url, r.status_code)
        except Exception as e:
            print(url, e)
        time.sleep(3)
    return ""


def main(site="dsg"):
    base = SITES[site]
    idx = get(base + "/seo_sitemap.xml")
    maps = re.findall(r"<loc>(.*?)</loc>", idx)
    prod_maps = [m for m in maps if "product" in m]
    print("sitemaps:", maps)
    rows = []
    for m in prod_maps:
        txt = get(m)
        blocks = re.findall(r"<url[^>]*>(.*?)</url>", txt, flags=re.S)
        for b in blocks:
            loc = re.search(r"<loc>(.*?)</loc>", b)
            if not loc:
                continue
            loc = loc.group(1).strip()
            lm = re.search(r"<lastmod>(.*?)</lastmod>", b)
            mm = re.search(r"/p/([^/]+)/([^/?#]+)", loc)
            slug, pid = (mm.group(1), mm.group(2)) if mm else ("", "")
            pref = pid[:2] if pid[:2].isdigit() else ""
            vend = pid[2:5] if pref else ""
            rows.append([loc, slug, pid, pref, vend, lm.group(1) if lm else "", m.rsplit("/", 1)[-1]])
        print(m, len(blocks))
        time.sleep(1)
    d = datetime.date.today().strftime("%Y%m%d")
    out = f"{RAW}\\X02_{site}_sitemap_urls_{d}.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["url", "slug", "pid", "year_prefix", "vendor_code", "lastmod", "sitemap"])
        w.writerows(rows)
    print("wrote", out, len(rows))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "dsg")
