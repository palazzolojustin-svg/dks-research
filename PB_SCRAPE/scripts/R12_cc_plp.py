"""R12 Common Crawl fallback: brand-facet owned share for the exact X02 census category pages, every CC crawl.

Uses CDX index files already downloaded by X03 (raw/X03_cc/<crawl>_f.jsonl = all dicks.com /f/ captures per crawl)
and R9 (raw/R9/idx/<crawl>_gg_f.jsonl = golfgalaxy.com /f/), so no index calls are needed. For each slug x crawl it
takes the HTTP-200 capture of the bare URL (no query string; falls back to a query variant only if it is a pure
pageNumber=0/sort param), range-fetches the WARC record from data.commoncrawl.org (polite: R9_cc_common throttle,
single thread), parses with R12_common.parse_plp and appends to raw/R12_cc_plp.csv.

Rerun: python PB_SCRAPE\\scripts\\R12_cc_plp.py [crawl-substring ...]   (resumable)
For new crawls: refresh the X03_cc / R9 idx files first (X03_cc_census.py / R9_cc_index.py) or add
cc_index_prefix() calls from R9_cc_common.
"""
import csv, glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("R9_CC_MIN_INTERVAL", "0.8")
from R9_cc_common import load_idx, fetch_warc
from R12_common import RAW, parse_plp, OWNED_BASE
from R12_wayback_plp import DKS, GG, COLS

OUT = os.path.join(RAW, "R12_cc_plp.csv")


def candidates(only):
    jobs = []
    srcs = [("dks", f, set(DKS)) for f in glob.glob(os.path.join(RAW, "X03_cc", "*_f.jsonl"))]
    srcs += [("gg", f, set(GG)) for f in glob.glob(os.path.join(RAW, "R9", "idx", "*_gg_f.jsonl"))]
    extra = load_idx(os.path.join(RAW, "R12_cc_idx_extra.jsonl"))
    for c in sorted({e["_crawl"] for e in extra}):
        for h, sl in (("dks", set(DKS)), ("gg", set(GG))):
            srcs.append((h, [e for e in extra if e["_crawl"] == c and e["_host"] == h], sl, c))
    for src in srcs:
        host, f, slugs = src[:3]
        crawl = src[3] if len(src) > 3 else os.path.basename(f)[:15]
        if only and not any(o in crawl for o in only):
            continue
        best = {}
        for r in (f if isinstance(f, list) else load_idx(f)):
            if str(r.get("status")) != "200":
                continue
            u = r["url"].split("://", 1)[-1]
            path = u.split("/", 1)[1] if "/" in u else ""
            base, q = (path.split("?", 1) + [""])[:2]
            base = base.rstrip("/")
            if not base.startswith("f/") or base[2:] not in slugs:
                continue
            slug = base[2:]
            rank = 0 if not q else (1 if all(k.split("=")[0] in ("pageNumber", "pageSize") for k in q.split("&")) else 9)
            if rank == 9:
                continue
            k = (host, slug)
            if k not in best or (rank, r["timestamp"]) < (best[k][0], best[k][1]["timestamp"]):
                best[k] = (rank, r)
        for (host, slug), (rank, r) in best.items():
            jobs.append((crawl, host, slug, r))
    return sorted(jobs, key=lambda j: j[0])


def main(only):
    done = set()
    if os.path.exists(OUT):
        for r in csv.DictReader(open(OUT, encoding="utf-8")):
            done.add((r["host"], r["slug"], r["ts"]))
    new = not os.path.exists(OUT)
    fh = open(OUT, "a", newline="", encoding="utf-8")
    w = csv.writer(fh)
    if new:
        w.writerow(COLS + ["crawl"])
    jobs = candidates(only)
    print("jobs", len(jobs), flush=True)
    for crawl, host, slug, r in jobs:
        if (host, slug, r["timestamp"]) in done:
            continue
        t = fetch_warc(r)
        p = parse_plp(t) if t else None
        if not p:
            print("  no data", crawl, host, slug, r["timestamp"], flush=True)
            continue
        b = p["brands"]
        tot = sum(b.values()) or None
        own = sum(v for k, v in b.items() if k in OWNED_BASE)
        pr = p["products"]
        row = [host, slug, r["timestamp"], crawl, "default", r["url"], p["layout"], p["total"], p["sort"], p["store"],
               p["pagesize"], tot, own, round(100 * own / tot, 2) if tot else None, sum(x[2] for x in pr[:24]),
               min(24, len(pr)), sum(x[2] for x in pr), len(pr), "|".join(sorted({x[1] for x in pr if x[2]})),
               json.dumps(dict(sorted(b.items(), key=lambda kv: -kv[1]))), crawl]
        w.writerow(row)
        fh.flush()
        print("  OK", crawl, host, slug, r["timestamp"], "total", p["total"], "owned%", row[13], "first24", row[14], flush=True)
    fh.close()
    print("DONE", flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
