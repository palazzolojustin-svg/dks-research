"""R12: harvest Wayback PLP pages that X03's job (X03_plp.py) already cached in raw/X03_cache (md5-named), so they can
be parsed with R12's two-layout parser (X03's own facet parser returns brands=0 on these pages).
Maps cache files back to (slug, timestamp) via raw/X03_plp.log lines + md5(f"{ts} {url}") over URL spellings.
Writes raw/R12_x03_harvest.csv (same columns as R12_wb_plp.csv). Rerun any time: python R12_harvest_x03.py
"""
import csv, hashlib, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from R12_common import RAW, parse_plp, OWNED_BASE
from R12_wayback_plp import COLS

pairs, slug = [], None
for l in open(os.path.join(RAW, "X03_plp.log"), encoding="utf-8", errors="replace"):
    m = re.match(r"(\S+/\S+) periods:", l.strip())
    if m:
        slug = m.group(1)
        continue
    m = re.match(r"\s*(\d{4}Q\d|\d{6})\s+(\d{14})\s+total=", l)
    if m and slug:
        pairs.append((slug, m.group(2)))
rows = []
for slug, ts in pairs:
    hit = None
    for pre in ("https://www.", "http://www.", "https://", "http://"):
        for suf in ("", "/"):
            for port in ("", ":443", ":80"):
                url = f"{pre.split('//')[0]}//{pre.split('//')[1]}dickssportinggoods.com{port}/{slug}{suf}"
                fn = os.path.join(RAW, "X03_cache", hashlib.md5(f"{ts} {url}".encode()).hexdigest() + ".html")
                if os.path.exists(fn):
                    hit = (fn, url)
    if not hit:
        print("no cache match", slug, ts)
        continue
    p = parse_plp(open(hit[0], encoding="utf-8", errors="replace").read())
    if not p:
        print("no data", slug, ts)
        continue
    b = p["brands"]; tot = sum(b.values()) or None; own = sum(v for k, v in b.items() if k in OWNED_BASE)
    pr = p["products"]
    s = slug.split("/", 1)[1]
    rows.append(["dks", s, ts, "x03", "default", hit[1], p["layout"], p["total"], p["sort"], p["store"], p["pagesize"],
                 tot, own, round(100 * own / tot, 2) if tot else None, sum(x[2] for x in pr[:24]), min(24, len(pr)),
                 sum(x[2] for x in pr), len(pr), "|".join(sorted({x[1] for x in pr if x[2]})),
                 json.dumps(dict(sorted(b.items(), key=lambda kv: -kv[1])))])
    print(s, ts, p["layout"], p["total"], "brands", len(b), "owned%", rows[-1][13], "first24", rows[-1][14])
with open(os.path.join(RAW, "R12_x03_harvest.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh); w.writerow(COLS); w.writerows(rows)
