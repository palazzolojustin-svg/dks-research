"""X03: owned-brand share of dicks.com product URLs seen in each Common Crawl crawl.

Reads raw/X03_cc/<collection>_p.jsonl (X03_cc_census.py with prefix www.dickssportinggoods.com/p/*).
Product URL = /p/<brand-slug>-<name>-<PID>/<PID>. Brand = leading slug tokens matched against OWNED list;
benchmarks are also tallied. A crawl's set of product URLs is a (link-graph-driven) sample of the live
catalogue, so owned share of distinct PIDs per crawl approximates owned share of SKU-styles listed.
Also reports the share of PIDs whose 2-digit year code equals the crawl year or previous year ("fresh").
Output: raw/X03_cc_pshare.csv
Usage: python X03_cc_pshare.py [status_filter e.g. 200|all]
"""
import sys, os, re, json, glob, csv, collections

RAW = os.path.join(os.path.dirname(__file__), "..", "raw")
OWNED = ["calia", "vrst", "dsg", "maxfli", "walter-hagen", "alpine-design", "ethos", "fitness-gear", "nishiki", "quest", "top-flite", "tommy-armour"]
BENCH = ["nike", "jordan", "adidas", "under-armour", "the-north-face", "columbia", "new-balance", "hoka", "on", "brooks", "asics", "titleist", "callaway", "taylormade",
         "yeti", "stanley", "carhartt", "champion", "puma", "lululemon", "vuori", "rawlings", "wilson", "easton", "coleman", "bowflex", "nordictrack"]
PID_RX = re.compile(r"/p/([^/?#]+)/([0-9]{2}[a-z0-9]+)", re.I)


def brand_of(slug):
    for b in sorted(OWNED + BENCH, key=len, reverse=True):
        if slug.startswith(b + "-"):
            return b
    return "_other"


def main(status="all"):
    out = []
    for fn in sorted(glob.glob(os.path.join(RAW, "X03_cc", "*_p.jsonl"))):
        coll = os.path.basename(fn).split("_")[0]
        pids = {}
        for l in open(fn, encoding="utf-8"):
            try:
                r = json.loads(l)
            except Exception:
                continue
            if status != "all" and r.get("status") != status:
                continue
            m = PID_RX.search(r["url"])
            if not m:
                continue
            pids[m.group(2).lower()] = (brand_of(m.group(1).lower()), r["timestamp"])
        n = len(pids)
        if n == 0:
            continue
        cnt = collections.Counter(b for b, _ in pids.values())
        own = sum(cnt[b] for b in OWNED)
        yr = coll.split("-")[2]
        ycode = {p[:2] for p in pids}
        fresh_all = sum(1 for p in pids if p[:2] in (yr[2:], str(int(yr) - 1)[2:]))
        fresh_own = sum(1 for p, (b, _) in pids.items() if b in OWNED and p[:2] in (yr[2:], str(int(yr) - 1)[2:]))
        row = {"collection": coll, "n_pids": n, "owned": own, "owned_share": round(own / n, 4),
               "fresh_share_all": round(fresh_all / n, 3), "fresh_share_owned": round(fresh_own / own, 3) if own else "",
               **{b: cnt[b] for b in OWNED + BENCH}, "_other": cnt["_other"]}
        out.append(row)
        print(coll, n, own, f"{own / n:.3%}", {b: cnt[b] for b in OWNED if cnt[b]}, "nike", cnt["nike"], flush=True)
    with open(os.path.join(RAW, f"X03_cc_pshare_{status}.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "all")
