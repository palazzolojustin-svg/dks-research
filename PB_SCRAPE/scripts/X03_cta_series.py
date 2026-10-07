"""X03: monthly series of dicks.com mega-menu "Featured" CTA slots, owned vs national brands,
split into feature/newness slots vs discount slots.

Sources (only already-cached HTML is used; run X03_home.py / X03_cc_plp.py / X03_cc_cta_fetch.py first):
  - Wayback homepage snapshots listed in raw/X03_cdx_home200.txt (cache raw/X03_cache)
  - Common Crawl captures listed in raw/X03_cc/*_f.jsonl (cache raw/X03_cc_cache)
For each calendar month, pools the distinct CTA (title, link) pairs from up to 3 snapshots.
Outputs raw/X03_cta_series.csv and raw/X03_cta_owned_titles.txt
Usage: python X03_cta_series.py
"""
import os, sys, re, json, glob, hashlib, csv, collections
sys.path.insert(0, os.path.dirname(__file__))
from X03_navcta import ctas, classify, DISC

RAW = os.path.join(os.path.dirname(__file__), "..", "raw")


def wb_cached():
    for l in open(os.path.join(RAW, "X03_cdx_home200.txt"), encoding="utf-8-sig"):
        p = l.split()
        if len(p) < 2 or not p[0][:1].isdigit():
            continue
        fn = os.path.join(RAW, "X03_cache", hashlib.md5(f"{p[0]} {p[1]}".encode()).hexdigest() + ".html")
        if os.path.exists(fn):
            yield p[0], "wb", fn


def cc_cached():
    for f in sorted(glob.glob(os.path.join(RAW, "X03_cc", "*_f.jsonl"))):
        for l in open(f, encoding="utf-8"):
            try:
                r = json.loads(l)
            except Exception:
                continue
            fn = os.path.join(RAW, "X03_cc_cache", hashlib.md5((r["filename"] + r["offset"]).encode()).hexdigest() + ".html")
            if os.path.exists(fn):
                yield r["timestamp"], "cc", fn


def main():
    bym = collections.defaultdict(list)
    for ts, src, fn in list(wb_cached()) + list(cc_cached()):
        bym[ts[:6]].append((ts, src, fn))
    rows = []
    log = open(os.path.join(RAW, "X03_cta_owned_titles.txt"), "w", encoding="utf-8")
    for m in sorted(bym):
        snaps = sorted(bym[m])
        pick = [snaps[i] for i in sorted({0, len(snaps) // 2, len(snaps) - 1})]
        pool = {}
        for ts, src, fn in pick:
            html = open(fn, encoding="utf-8", errors="replace").read()
            for title, link in ctas(html):
                if link.startswith(("/s/terms", "/s/privacy", "/s/web-content", "/s/donotsell", "/s/california", "/TrackOrder", "/MyAccount")):
                    continue
                pool[(title.strip(), link.split("?")[0] if "X_BRAND" not in link else link)] = None
        c = collections.Counter()
        owned_titles = []
        for (title, link) in pool:
            k = classify(title, link)
            d = "disc" if DISC.search(title + " " + link) else "feat"
            c[f"{k}_{d}"] += 1
            if k == "own":
                owned_titles.append(f"{d}: {title} [{link}]")
        own = c["own_feat"] + c["own_disc"]
        nat = c["nat_feat"] + c["nat_disc"]
        row = {"month": m, "snapshots": len(pick), "sources": "+".join(sorted({s for _, s, _ in pick})), "cta_total": len(pool),
               "own_feat": c["own_feat"], "own_disc": c["own_disc"], "nat_feat": c["nat_feat"], "nat_disc": c["nat_disc"],
               "own_share_brand_ctas": round(own / (own + nat), 3) if own + nat else "",
               "own_share_feature_ctas": round(c["own_feat"] / (c["own_feat"] + c["nat_feat"]), 3) if c["own_feat"] + c["nat_feat"] else ""}
        rows.append(row)
        log.write(f"== {m} {row}\n" + "".join(f"   {t}\n" for t in owned_titles))
        print(m, row["sources"], "tot", len(pool), "own f/d", c["own_feat"], c["own_disc"], "nat f/d", c["nat_feat"], c["nat_disc"], "share", row["own_share_brand_ctas"])
    log.close()
    with open(os.path.join(RAW, "X03_cta_series.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)


if __name__ == "__main__":
    main()
