"""X03: matched-page y/y panel of dicks.com PLPs from Common Crawl (same URL, base window vs compare window).

Input: slug file (from X03_cc_pairs.py, optionally filtered), base and compare collection lists.
For each slug: picks the latest HTTP-200 capture in each window, fetches (cached), parses totalCount, Sale facet,
brand facet (X_BRAND, when rendered) and the brand of each product card (mfName / X_BRAND JSON, page order).
Output: raw/X03_cc_panel_<tag>.csv
Usage: python X03_cc_panel.py <slugfile> <base colls> <cmp colls> <tag> [slug-include-regex] [slug-exclude-regex]
"""
import os, sys, re, json, csv, hashlib, collections
sys.path.insert(0, os.path.dirname(__file__))
from X03_cc import cc_fetch
from X03_plp import parse

RAW = os.path.join(os.path.dirname(__file__), "..", "raw")
CACHE = os.path.join(RAW, "X03_cc_cache")
OWN = re.compile(r"^(CALIA|CALIA by Carrie Underwood|VRST|DSG|Maxfli|MAXFLI|Walter Hagen|Alpine Design|ETHOS|Fitness Gear|Nishiki|Quest|Top Flite|Top-Flite|Tommy Armour)$", re.I)


def caps(colls, want):
    best = {}
    for c in colls:
        fn = os.path.join(RAW, "X03_cc", f"{c}_f.jsonl")
        if not os.path.exists(fn):
            continue
        for l in open(fn, encoding="utf-8"):
            try:
                r = json.loads(l)
            except Exception:
                continue
            if r.get("status") != "200" or "?" in r["url"]:
                continue
            s = re.sub(r"^https?://[^/]+/", "", r["url"]).rstrip("/").lower()
            if s in want and (s not in best or r["timestamp"] > best[s]["timestamp"]):
                best[s] = r
    return best


def html_of(r):
    fn = os.path.join(CACHE, hashlib.md5((r["filename"] + r["offset"]).encode()).hexdigest() + ".html")
    if os.path.exists(fn):
        return open(fn, encoding="utf-8", errors="replace").read()
    t = cc_fetch(r["filename"], r["offset"], r["length"])
    if t:
        open(fn, "w", encoding="utf-8").write(t)
    return t


def cards(html):
    b = re.findall(r'"mfName":"([^"]{1,40})"', html)
    if b:
        # each product appears in two JSON blobs on the 2025-26 template; keep first half if duplicated
        half = len(b) // 2
        if half and b[:half] == b[half:2 * half]:
            b = b[:half]
        return b
    return re.findall(r'\\"X_BRAND\\":\\"([^\\"]+)\\"', html)


def summarise(html):
    total, fac = parse(html)
    br = fac.get("X_BRAND", {})
    own_f = sum(v for k, v in br.items() if OWN.match(k.strip()))
    sale = None
    for a in ("5004",):
        if a in fac:
            sale = sum(fac[a].values())
    cb = cards(html)
    own_c = sum(1 for x in cb if OWN.match(x.strip()))
    return {"total": total, "sale": sale, "facet_sum": sum(br.values()) if br else None, "facet_owned": own_f if br else None,
            "n_brands": len(br) if br else None, "cards": len(cb), "cards_owned": own_c,
            "owned_detail": ";".join(f"{k}:{v}" for k, v in br.items() if OWN.match(k.strip()))}


def main(slugfile, base, cmp_, tag, inc=None, exc=None):
    want = [l.strip() for l in open(slugfile) if l.strip()]
    if inc:
        want = [s for s in want if re.search(inc, s)]
    if exc:
        want = [s for s in want if not re.search(exc, s)]
    want = set(want)
    print("slugs", len(want), flush=True)
    b, c = caps(base.split(","), want), caps(cmp_.split(","), want)
    fn = os.path.join(RAW, f"X03_cc_panel_{tag}.csv")
    done = set()
    if os.path.exists(fn):
        done = {r["slug"] for r in csv.DictReader(open(fn, encoding="utf-8"))}
    fh = open(fn, "a", newline="", encoding="utf-8")
    cols = ["slug", "ts_base", "ts_cmp"] + [f"{k}_{w}" for w in ("base", "cmp") for k in ("total", "sale", "facet_sum", "facet_owned", "n_brands", "cards", "cards_owned", "owned_detail")]
    w = csv.DictWriter(fh, fieldnames=cols)
    if not done:
        w.writeheader()
    for s in sorted(want):
        if s in done or s not in b or s not in c:
            continue
        hb, hc = html_of(b[s]), html_of(c[s])
        if not hb or not hc:
            continue
        sb, sc = summarise(hb), summarise(hc)
        row = {"slug": s, "ts_base": b[s]["timestamp"], "ts_cmp": c[s]["timestamp"]}
        row.update({f"{k}_base": v for k, v in sb.items()})
        row.update({f"{k}_cmp": v for k, v in sc.items()})
        w.writerow(row)
        fh.flush()
        print(s, sb["total"], "->", sc["total"], "| own facet", sb["facet_owned"], "->", sc["facet_owned"], "| sale", sb["sale"], "->", sc["sale"], flush=True)
    fh.close()


if __name__ == "__main__":
    a = sys.argv
    main(a[1], a[2], a[3], a[4], a[5] if len(a) > 5 else None, a[6] if len(a) > 6 else None)
