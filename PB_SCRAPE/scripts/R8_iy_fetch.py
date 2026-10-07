"""R8: polite ImportYeti fetcher (free public pages, no login) with caching.

Usage:
    python R8_iy_fetch.py company academy kohls ...
    python R8_iy_fetch.py supplier foremost-golf-mfg makalot-garments-cambodia
    python R8_iy_fetch.py search "hibbett"
    python R8_iy_fetch.py dmsc_suppliers      # every supplier on the DMSC company page (from X04/R8 payload)
Saves the decoded Next.js RSC payload to PB_SCRAPE/raw/R8_iy_<kind>_<slug>.txt (skips if fetched today unless --force).
Waits 15s between requests; if the page comes back as an empty shell (soft block), waits 120s and retries once.
"""
import re, sys, os, time, datetime, glob
import requests

RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "raw")
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36",
     "Accept": "text/html,application/xhtml+xml", "Accept-Language": "en-US,en;q=0.9"}
SPACING = 20


def decode(html):
    chunks = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)</script>', html, re.S)
    big = "".join(chunks).encode().decode("unicode_escape", errors="ignore")
    try:
        big = big.encode("latin-1", errors="ignore").decode("utf-8", errors="ignore")
    except Exception:
        pass
    return big


def path_for(kind, slug):
    safe = re.sub(r"[^A-Za-z0-9_-]+", "_", slug)[:70]
    return os.path.join(RAW, f"R8_iy_{kind}_{safe}.txt")


def fetch(kind, slug, force=False):
    p = path_for(kind, slug)
    if os.path.exists(p) and not force and os.path.getsize(p) > 20000:
        if datetime.date.fromtimestamp(os.path.getmtime(p)) == datetime.date.today():
            return open(p, encoding="utf-8").read(), "cached"
    url = f"https://www.importyeti.com/{kind}/{slug}" if kind != "search" else f"https://www.importyeti.com/search?q={requests.utils.quote(slug)}"
    for attempt in range(4):
        try:
            r = requests.get(url, headers=H, timeout=60)
            big = decode(r.text)
        except Exception as e:
            big, r = "", None
        ok = ("Over Time" in big) or kind == "search"
        if ok:
            open(p, "w", encoding="utf-8").write(big)
            time.sleep(SPACING)
            return big, (r.status_code if r is not None else "ERR")
        if "4 Not Found" in big and attempt >= 1:
            # genuine 404s persist; soft-blocks also show 404 -> retry a few times before giving up
            pass
        time.sleep(150 * (attempt + 1))
    return "", "fail(soft-block or 404)"


def dmsc_supplier_slugs():
    srcs = sorted(glob.glob(os.path.join(RAW, "R8_iy_company_dick-s-merchandising-and-supply-cha.txt"))) + \
        [os.path.join(RAW, "X04_iy_company_dick-s-merchandising-and-supply-cha.txt"), os.path.join(RAW, "X04_wayback_dmsc_20250906_rsc.txt")]
    slugs = []
    for s in srcs:
        if os.path.exists(s):
            for m in re.finditer(r'"vendor_name":"[^"]*".*?"url":"/supplier/([^"]*)"', open(s, encoding="utf-8").read()):
                if m.group(1) not in slugs:
                    slugs.append(m.group(1))
    return slugs


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--force"]
    force = "--force" in sys.argv
    kind = args[0]
    if kind == "dmsc_suppliers":
        targets = [("supplier", s) for s in dmsc_supplier_slugs()]
    else:
        targets = [(kind, s) for s in args[1:]]
    for k, s in targets:
        big, st = fetch(k, s, force)
        print(k, s, st, len(big), flush=True)
