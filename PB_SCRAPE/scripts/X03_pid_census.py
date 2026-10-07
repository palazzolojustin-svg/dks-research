"""X03: dicks.com product-ID census from the Wayback Machine CDX index.

Idea: dicks.com product URLs look like
  https://www.dickssportinggoods.com/p/<brand-slug>-<name>-<PID>/<PID>
where PID begins with a 2-digit season-year code (e.g. 24maxwclxmxfl2024bag = 2024).
Every distinct PID ever seen by the Wayback crawler (any HTTP status, even 403 blocks,
since the crawler only needs to have discovered the link) is a SKU-style that existed.
Counting distinct PIDs by brand-slug and year code gives an assortment-creation time
series by brand; normalising owned brands against national brands in the same year
cohort controls for changes in crawl intensity.

Usage:
  python X03_pid_census.py            # pulls every brand in BRANDS, writes raw/X03_pid_<brand>.txt
  python X03_pid_census.py calia vrst # only those brands
Then run X03_pid_summary.py to build the table.
Rerun weekly/monthly: the CDX index grows as new captures are made.
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(__file__))
from X03_wb import get

OUT = os.path.join(os.path.dirname(__file__), "..", "raw")
HOSTS = ["www.dickssportinggoods.com", "www.golfgalaxy.com"]
BRANDS = [
    # owned
    "calia", "vrst", "dsg", "maxfli", "walter-hagen", "alpine-design", "ethos", "fitness-gear",
    "nishiki", "quest", "top-flite", "tommy-armour",
    # benchmarks (national brands)
    "nike", "under-armour", "adidas", "the-north-face", "columbia", "new-balance", "hoka", "brooks",
    "titleist", "callaway", "taylormade", "lululemon", "vuori", "on", "champion", "puma", "yeti", "rawlings",
]


def cdx_pages(url):
    r = get("https://web.archive.org/cdx/search/cdx", params={"url": url, "showNumPages": "true"}, timeout=120)
    if r is None or r.status_code != 200:
        return None
    return int(r.text.strip() or 0)


def cdx_page(url, page):
    params = {"url": url, "fl": "timestamp,original,statuscode", "collapse": "urlkey", "page": str(page)}
    r = get("https://web.archive.org/cdx/search/cdx", params=params, timeout=240)
    if r is None or r.status_code != 200:
        return None
    return r.text


def run(brand):
    fn = os.path.join(OUT, f"X03_pid_{brand}.txt")
    if os.path.exists(fn) and os.path.getsize(fn) > 0:
        print(brand, "exists, skip")
        return
    lines = []
    ok = True
    for host in HOSTS:
        url = f"{host}/p/{brand}-*"
        n = cdx_pages(url)
        print(brand, host, "pages", n, file=sys.stderr)
        if n is None:
            ok = False
            continue
        for p in range(max(n, 1)):
            t = cdx_page(url, p)
            if t is None:
                ok = False
                continue
            lines.append(t)
    with open(fn + (".partial" if not ok else ""), "w", encoding="utf-8") as f:
        f.write("".join(lines))
    print(brand, "done", sum(x.count("\n") for x in lines), "rows", "OK" if ok else "PARTIAL")


if __name__ == "__main__":
    for b in (sys.argv[1:] or BRANDS):
        run(b)
