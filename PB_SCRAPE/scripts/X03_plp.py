"""X03: dicks.com product-listing-page (PLP) facet history from the Wayback Machine.

For each PLP slug, lists Wayback captures (HTTP 200, exact URL, no query string) since 2022,
picks one capture per quarter (largest compressed size), fetches the raw HTML and extracts:
  - totalCount (number of products on the page/category)
  - every facet value count, notably X_BRAND (brand) and Sale (5004/"Sale")
Handles the 2022-24 layout (input id=checkbox_<ATTR>_<i> title=<value> ... "(N)") and the
2025-26 layout (aria-label="<value>, N products" id=homefield-checkbox-<ATTR>-<value>).
Output (long format): raw/X03_plp_facets.csv  [slug, ts, quarter, total, attr, value, count]
Usage:
  python X03_plp.py slugs.txt [per=quarter|month] [from=2022]
  slugs.txt = one slug per line (e.g. f/womens-athletic-leggings, f/golf-balls, c/dicks-exclusive-brands)
Re-run any time: cached snapshots are reused; new quarters are appended.
"""
import sys, os, re, csv, json
from bs4 import BeautifulSoup as B
sys.path.insert(0, os.path.dirname(__file__))
from X03_fetch import fetch
from X03_cdx import cdx

RAW = os.path.join(os.path.dirname(__file__), "..", "raw")
HOST = "https://www.dickssportinggoods.com/"


def parse(html):
    out = {}
    m = re.search(r'"totalCount"\s*:\s*(\d+)', html)
    total = int(m.group(1)) if m else None
    if total is None:
        m = re.search(r'(\d[\d,]*) Products</span>', html)
        total = int(m.group(1).replace(",", "")) if m else None
    # 2025-26 layout
    for m in re.finditer(r'aria-label="([^"]+?), (\d+) products?"[^>]*?id="?homefield-checkbox-([A-Za-z0-9_]+?)-', html):
        val, n, attr = m.group(1), int(m.group(2)), m.group(3)
        out.setdefault(attr, {})[val.replace("&amp;", "&")] = n
    if not out:
        # 2022-24 layout
        s = B(html, "html.parser")
        for inp in s.find_all("input", id=re.compile(r"^checkbox_")):
            mid = re.match(r"checkbox_(.+)_(\d+)$", inp.get("id", ""))
            if not mid:
                continue
            attr, val = mid.group(1), inp.get("title", "")
            par = inp.parent
            cnt = None
            for _ in range(4):
                if par is None:
                    break
                mm = re.search(r"\((\d+)\)", par.get_text(" ", strip=True))
                if mm:
                    cnt = int(mm.group(1))
                    break
                par = par.parent
            if cnt is not None:
                out.setdefault(attr, {})[val] = cnt
    return total, out


def quarter(ts):
    return f"{ts[:4]}Q{(int(ts[4:6]) - 1) // 3 + 1}"


def run(slugs, per="quarter", frm="2022"):
    fn = os.path.join(RAW, "X03_plp_facets.csv")
    done = set()
    if os.path.exists(fn):
        for r in csv.DictReader(open(fn, encoding="utf-8")):
            done.add((r["slug"], r["ts"]))
    new = not os.path.exists(fn)
    fh = open(fn, "a", newline="", encoding="utf-8")
    w = csv.writer(fh)
    if new:
        w.writerow(["slug", "ts", "period", "total", "attr", "value", "count"])
    for slug in slugs:
        rows = cdx(HOST.replace("https://", "") + slug, frm, None, filter="statuscode:200")
        if not rows:
            print(slug, "no captures", flush=True)
            continue
        rows = [r for r in rows if r[3].isdigit() and int(r[3]) > 30000 and "?" not in r[1]]
        best = {}
        for r in rows:
            k = quarter(r[0]) if per == "quarter" else r[0][:6]
            # prefer the latest capture within the period (closest to period end), but large enough
            if k not in best or r[0] > best[k][0]:
                best[k] = r
        print(slug, "periods:", sorted(best), flush=True)
        for k in sorted(best):
            ts, url = best[k][0], best[k][1]
            if (slug, ts) in done:
                continue
            html = fetch(ts, url)
            if not html:
                print("  fail", ts, flush=True)
                continue
            total, fac = parse(html)
            brands = fac.get("X_BRAND", {})
            print(f"  {k} {ts} total={total} brands={len(brands)}", flush=True)
            w.writerow([slug, ts, k, total, "_TOTAL", "", total])
            for attr, vals in fac.items():
                if attr in ("X_BRAND", "5004") or attr.lower().startswith("sale") or any(v.lower() == "sale" for v in vals):
                    for v, n in vals.items():
                        w.writerow([slug, ts, k, total, attr, v, n])
            fh.flush()
    fh.close()


if __name__ == "__main__":
    slugs = [l.strip() for l in open(sys.argv[1]) if l.strip() and not l.startswith("#")]
    run(slugs, sys.argv[2] if len(sys.argv) > 2 else "quarter", sys.argv[3] if len(sys.argv) > 3 else "2022")
