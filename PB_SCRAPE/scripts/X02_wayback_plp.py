"""X02: extract the embedded product-list API response from ARCHIVED dicks.com listing pages (Wayback),
to compare owned-brand share of listings / default-sort placement / brand facets over time.

Archived pages (2025+) embed an Angular transfer-state JSON blob in which one entry's body ("b") holds
{totalCount, searchVO, productVOs (with attribute 6025 'Vertical Brand'), facetVOs (X_BRAND counts)}.
Note: archived captures are default sort (Featured, selectedSort=5), first page (48 items) only.

Rerun: python PB_SCRAPE\\scripts\\X02_wayback_plp.py <category-slug> [<category-slug> ...]
   - lists captures via CDX (from 2024), downloads each (cached in raw\\X02_wb_cache), prints and
     appends rows to raw\\X02_wb_plp_summary.csv
"""
import sys, os, re, json, time, csv, requests

RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\PB_SCRAPE\raw"
CACHE = RAW + r"\X02_wb_cache"
os.makedirs(CACHE, exist_ok=True)
OWN = {"DSG", "CALIA", "VRST", "Maxfli", "MAXFLI", "Walter Hagen", "Top Flite", "Tommy Armour Golf", "Alpine Design",
       "ETHOS", "Fitness Gear", "Nishiki", "Quest", "PRIMED", "Tour Trek", "DICK'S Sporting Goods"}


def get(u, tries=6):
    for i in range(tries):
        try:
            r = requests.get(u, timeout=120, headers={"User-Agent": "Mozilla/5.0 research X02"})
            if r.status_code == 200:
                return r.text
        except Exception:
            pass
        time.sleep(15 * (i + 1))
    return ""


def find_resp(t):
    for m in re.finditer(r"<script[^>]*>(.*?)</script>", t, re.S):
        s = m.group(1)
        if '"searchVO"' not in s or '"productVOs"' not in s:
            continue
        try:
            j = json.loads(s)
        except Exception:
            continue
        stack = [j]
        while stack:
            x = stack.pop()
            if isinstance(x, dict):
                if "productVOs" in x and "totalCount" in x:
                    return x
                stack.extend(x.values())
            elif isinstance(x, list):
                stack.extend(x)
    return None


def analyze(cat, ts, t):
    R = find_resp(t)
    if not R:
        return None
    pv = R.get("productVOs") or []
    flags = ["Vertical Brand" in (p.get("attributes") or "") for p in pv]
    brands = {}
    for f in R.get("facetVOs") or []:
        if f.get("attrIdentifier") == "X_BRAND":
            brands = f.get("values") or {}
    own_fac = sum(v for k, v in brands.items() if k in OWN)
    tot_fac = sum(brands.values()) or None
    return [cat, ts, R.get("totalCount"), (R.get("searchVO") or {}).get("selectedSort"), len(pv),
            sum(flags[:24]), min(24, len(pv)), sum(flags), own_fac, tot_fac,
            round(100 * own_fac / tot_fac, 1) if tot_fac else None,
            json.dumps({k: v for k, v in sorted(brands.items(), key=lambda x: -x[1])[:15]})]


def main(cats):
    out = RAW + r"\X02_wb_plp_summary.csv"
    new = not os.path.exists(out)
    with open(out, "a", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        if new:
            w.writerow(["cat", "ts", "totalCount", "sort", "n_items", "owned_in_first24", "first24_n", "owned_in_page",
                        "owned_facet_count", "all_facet_count", "owned_facet_pct", "top_brands"])
        for cat in cats:
            cdx = get(f"https://web.archive.org/cdx/search/cdx?url=dickssportinggoods.com/f/{cat}&from=2024&output=json"
                      f"&fl=timestamp,statuscode&filter=statuscode:200&collapse=timestamp:6")
            try:
                caps = [r[0] for r in json.loads(cdx)[1:]]
            except Exception:
                caps = []
            print(cat, "captures", caps)
            for ts in caps:
                fp = f"{CACHE}\\plp_{cat}_{ts}.html"
                if os.path.exists(fp):
                    t = open(fp, encoding="utf-8").read()
                else:
                    t = get(f"https://web.archive.org/web/{ts}id_/https://www.dickssportinggoods.com/f/{cat}")
                    if t:
                        open(fp, "w", encoding="utf-8").write(t)
                    time.sleep(4)
                row = analyze(cat, ts, t) if t else None
                print(" ", ts, row[:11] if row else "no embedded response")
                if row:
                    w.writerow(row)


if __name__ == "__main__":
    main(sys.argv[1:])
