"""R12: Wayback y/y owned-brand share of listed products for ALL X02 census categories (dicks.com 40 + golfgalaxy.com 5).

What it does
  1. CDX (prefix match, so query-string variants such as ?selectedSort=1 "Top Sellers" are found too) for every slug,
     saved to raw/R12_cdx/<host>_<slug>.json  (skipped if already saved; delete the file to refresh).
  2. Picks, per slug, the HTTP-200 capture nearest each target window (priority order below) and fetches it in
     id_ mode (raw HTML), caching to raw/R12_wb_cache/. Re-uses X02's cache (raw/X02_wb_cache/plp_<slug>_<ts>.html).
  3. Parses with R12_common.parse_plp (both the 2023-24 window.__STATE__ layout and the 2025-26 ngx layout) and appends
     one row per capture to raw/R12_wb_plp.csv (brand facet counts -> owned share; DKS 6025 'Vertical Brand' flag on the
     first page -> owned share of the first 24 default-sort slots).

Windows (priority order): W25B Jul15-Oct-2025 (target 25-Aug-2025), W24A Feb-May-2024 (15-Apr-2024),
  W26B Jul-Oct-2026, W24B mid-Jun-Oct-2024, W25A Feb-Jun-2025, W26A Feb-Jun-2026, W23 Jun-2023-Jan-2024.
  Plus every month that has a "selectedSort=1" (Top Sellers) capture.

Rerun:   python PB_SCRAPE\\scripts\\R12_wayback_plp.py            (all slugs; resumable; cached pages re-used)
         python PB_SCRAPE\\scripts\\R12_wayback_plp.py golf-balls bikes   (subset)
Then:    python PB_SCRAPE\\scripts\\R12_build_table.py
Wayback throttles hard when several jobs share an IP: the shared stamp file (raw/X03_last_request.txt) + exponential
back-off (60 s -> 15 min) keeps this polite. Expect ~1-5 min per page under contention. Do not parallelise.
"""
import csv, json, os, sys, time
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from R12_common import RAW, wb_get, parse_plp, OWNED_BASE

DKS = ['womens-athletic-leggings', 'sports-bras', 'shop-womens-joggers', 'womens-shorts-1', 'womens-jackets-vests',
       'womens-shirts-tops', 'girls-leggings', 'girls-shirts-tops', 'boys-shirts-tops', 'boys-shorts', 'mens-shirts',
       'mens-shorts', 'mens-pants', 'mens-joggers', 'mens-golf-apparel', 'womens-golf-apparel', 'golf-balls',
       'golf-clubs', 'golf-drivers', 'putters', 'golf-wedges', 'golf-bags-accessories-1', 'golf-gloves',
       'mens-running-shoes', 'womens-running-shoes', 'baseball-bats', 'baseball-gloves', 'all-soccer-balls',
       'basketballs', 'camping-family-tents', 'sleeping-bags', 'camping-coolers', 'backpacks-duffle-bags',
       'water-bottles-hydration', 'bikes', 'dumbbells', 'weight-benches', 'strength-training-equipment', 'treadmills',
       'yoga-mats']
GG = ['golf-ball-dozens', 'golf-clothes-apparel-for-men', 'womens-golf-clothes-and-apparel', 'shop-drivers',
      'golf-irons-sets']
HOSTS = {"dks": "www.dickssportinggoods.com", "gg": "www.golfgalaxy.com"}

WINDOWS = [("W25B", "20250715", "20251031", "20250825"), ("W24A", "20240201", "20240531", "20240415"),
           ("W26B", "20260701", "20261007", "20260825"), ("W24B", "20240615", "20241031", "20240820"),
           ("W25A", "20250201", "20250630", "20250415"), ("W26A", "20260201", "20260630", "20260415"),
           ("W23", "20230601", "20240131", "20231015")]

CDXDIR = os.path.join(RAW, "R12_cdx")
CACHE = os.path.join(RAW, "R12_wb_cache")
X02C = os.path.join(RAW, "X02_wb_cache")
OUT = os.path.join(RAW, "R12_wb_plp.csv")
LOG = os.path.join(RAW, "R12_wayback.log")
os.makedirs(CDXDIR, exist_ok=True)
os.makedirs(CACHE, exist_ok=True)
COLS = ["host", "slug", "ts", "window", "variant", "original", "layout", "total", "sort", "store", "pagesize",
        "facet_sum", "owned_facet", "owned_pct", "first24_own", "first24_n", "owned_in_page", "n_page",
        "flagged_brands", "brands_json"]


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write(datetime.now().strftime("%H:%M:%S ") + s + "\n")


def cdx(host, slug):
    fn = os.path.join(CDXDIR, f"{host}_{slug}.json")
    if os.path.exists(fn):
        return json.load(open(fn))
    r = wb_get("https://web.archive.org/cdx/search/cdx",
               {"url": f"{HOSTS[host]}/f/{slug}", "matchType": "prefix", "from": "2023", "output": "json",
                "fl": "timestamp,original,statuscode,length", "filter": "statuscode:200"}, log=log)
    if r is None or r.status_code != 200:
        log(host, slug, "CDX failed")
        return None
    try:
        rows = r.json()[1:] if r.text.strip() else []
    except Exception:
        rows = []
    # keep exact slug (path == /f/<slug>), with or without query string
    keep = []
    for ts, orig, st, ln in rows:
        path = orig.split("://", 1)[-1].split("/", 1)[-1]
        base = path.split("?", 1)[0].rstrip("/")
        if base == f"f/{slug}":
            keep.append([ts, orig, st, ln])
    json.dump(keep, open(fn, "w"))
    log(host, slug, "CDX", len(rows), "rows,", len(keep), "exact")
    return keep


def variant(orig):
    q = orig.split("?", 1)[1] if "?" in orig else ""
    if not q:
        return "default"
    if "selectedSort=1" in q:
        return "sort1"
    return "q:" + q[:60]


def choose(rows):
    """returns list of (window, ts, original, variant) in priority order"""
    out = []
    good = [r for r in rows if (r[3] or "0").isdigit() and int(r[3]) > 20000]
    dfl = [r for r in good if variant(r[1]) == "default"]
    for w, a, b, tgt in WINDOWS:
        cand = [r for r in dfl if a <= r[0][:8] <= b]
        if cand:
            t0 = datetime.strptime(tgt, "%Y%m%d")
            best = min(cand, key=lambda r: abs((datetime.strptime(r[0][:8], "%Y%m%d") - t0).days))
            out.append((w, best[0], best[1], "default"))
    seen = set()
    for r in sorted(good):
        if variant(r[1]) == "sort1" and r[0][:6] not in seen:
            seen.add(r[0][:6])
            out.append(("sort1", r[0], r[1], "sort1"))
    return out


def fetch(host, slug, ts, orig, var):
    tag = "" if var == "default" else "_" + var
    fn = os.path.join(CACHE, f"{host}_{slug}{tag}_{ts}.html")
    if os.path.exists(fn):
        return open(fn, encoding="utf-8", errors="replace").read()
    if host == "dks" and var == "default":
        x = os.path.join(X02C, f"plp_{slug}_{ts}.html")
        if os.path.exists(x):
            return open(x, encoding="utf-8", errors="replace").read()
    r = wb_get(f"https://web.archive.org/web/{ts}id_/{orig}", log=log)
    if r is None or r.status_code != 200:
        log("   fetch fail", host, slug, ts, r.status_code if r is not None else None)
        return None
    r.encoding = "utf-8"
    t = r.text
    open(fn, "w", encoding="utf-8").write(t)
    return t


def row(host, slug, ts, w, var, orig, p):
    b = p["brands"]
    tot = sum(b.values()) or None
    own = sum(v for k, v in b.items() if k in OWNED_BASE)
    pr = p["products"]
    return [host, slug, ts, w, var, orig, p["layout"], p["total"], p["sort"], p["store"], p["pagesize"], tot, own,
            round(100 * own / tot, 2) if tot else None, sum(x[2] for x in pr[:24]), min(24, len(pr)),
            sum(x[2] for x in pr), len(pr), "|".join(sorted({x[1] for x in pr if x[2]})),
            json.dumps(dict(sorted(b.items(), key=lambda kv: -kv[1])))]


def main(only):
    done = set()
    if os.path.exists(OUT):
        for r in csv.DictReader(open(OUT, encoding="utf-8")):
            done.add((r["host"], r["slug"], r["ts"], r["variant"]))
    new = not os.path.exists(OUT)
    fh = open(OUT, "a", newline="", encoding="utf-8")
    w = csv.writer(fh)
    if new:
        w.writerow(COLS)
    slugs = [("dks", s) for s in DKS] + [("gg", s) for s in GG]
    if only:
        slugs = [x for x in slugs if x[1] in only]
    # windows already covered by other archive sources (CC, X02/X03 caches) are skipped to save Wayback requests
    covered = set()
    try:
        from R12_build_table import load, period
        for o in load()[0]:
            if o.get("period") and o["src"] != "wayback":
                covered.add((o["host"], o["slug"], o["period"]))
    except Exception as e:
        log("coverage load failed", e)
    wmap = {"W25B": "25B", "W24A": "24A", "W26B": "26B", "W24B": "24B", "W25A": "25A", "W26A": "26A", "W23": "23H2"}
    # slugs X03_plp.py is already walking quarter by quarter go last
    x03 = set()
    try:
        x03 = {l.strip()[2:] for l in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "X03_plp_slugs.txt"))
               if l.startswith("f/")}
    except Exception:
        pass
    slugs = [x for x in slugs if x[1] not in x03] + [x for x in slugs if x[1] in x03]
    # phase 1: CDX for every slug
    plans = {}
    for host, slug in slugs:
        rows = cdx(host, slug)
        if rows:
            plans[(host, slug)] = choose(rows)
            log("  plan", host, slug, [(a, b[:8], d) for a, b, c, d in plans[(host, slug)]])
    # phase 2: fetch by priority rank across slugs (all W25B first, then W24A, ...)
    order = [x[0] for x in WINDOWS] + ["sort1"]
    for wname in order:
        for (host, slug), plan in plans.items():
            for (wn, ts, orig, var) in plan:
                if wn != wname or (host, slug, ts, var) in done:
                    continue
                if var == "default" and (host, slug, wmap.get(wn)) in covered:
                    continue
                t = fetch(host, slug, ts, orig, var)
                p = parse_plp(t) if t else None
                if not p:
                    log("   no embedded data", host, slug, ts, var)
                    continue
                rw = row(host, slug, ts, wn, var, orig, p)
                w.writerow(rw)
                fh.flush()
                done.add((host, slug, ts, var))
                log("  OK", wn, host, slug, ts, var, "total", rw[7], "owned%", rw[13], "first24", rw[14], "flags", rw[18])
    fh.close()
    log("DONE")


if __name__ == "__main__":
    main(set(sys.argv[1:]))
