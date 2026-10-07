"""R12: brand-facet owned share on R9's large matched panel of dicks.com category pages (Common Crawl), by window.

R9 (wave 2) extracts every page of its matched URL panel (raw/R9/cc/<crawl>_panel_pages.jsonl, with the full facet
dict incl. Brand/X_BRAND counts). R9 measures owned share of product SLOTS shown; this script measures owned share of
the whole category's listed products (brand facet), i.e. the R12/X02 metric, on the same pages. No new fetching.
Windows: W23 = CC-MAIN-2023-40/2023-50/2024-10 (Sep-23..Mar-24), W25 = 2025-33/2025-38 (Aug-Sep-25),
         W26 = 2026-34/2026-39 (Aug-Sep-26). One capture per URL per window (first crawl listed wins).
Page filter: URL has a brand facet with >=3 brands in both windows (excludes single-brand and fan-team pages) and the
slug does not contain 'x-brand' (brand-filtered pages). R9's catgroup/mixed labels are joined from raw/R9_panel_pages.csv.
Rerun (after R9 extraction finishes): python PB_SCRAPE\\scripts\\R12_panel_facets.py
Output: raw/R12_panel_facets.csv (url x window), printed pooled / LFL / by-catgroup summaries.
"""
import ast, csv, json, os, sys
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from R12_common import RAW, OWNED_BASE

WIN = {"W23": ["CC-MAIN-2023-40", "CC-MAIN-2023-50", "CC-MAIN-2024-10"], "W25": ["CC-MAIN-2025-33", "CC-MAIN-2025-38"],
       "W26": ["CC-MAIN-2026-34", "CC-MAIN-2026-39"]}
owned = OWNED_BASE | {"Lady Hagen"}
cat = {}
try:
    for r in csv.DictReader(open(os.path.join(RAW, "R9_panel_pages.csv"), encoding="utf-8")):
        cat[r["url"]] = r["catgroup"]
except Exception:
    pass
data = defaultdict(dict)
for w, crawls in WIN.items():
    for c in crawls:
        fn = os.path.join(RAW, "R9", "cc", f"{c}_panel_pages.jsonl")
        if not os.path.exists(fn):
            continue
        for l in open(fn, encoding="utf-8"):
            try:
                j = json.loads(l)
                fac = j.get("facets") or {}
                if isinstance(fac, str):
                    fac = ast.literal_eval(fac) if fac not in ("None", "") else {}
            except Exception:
                continue
            b = None
            for k, v in fac.items():
                if isinstance(v, dict) and v.get("id") == "X_BRAND":
                    b = {kk: int(vv) for kk, vv in v["vals"].items()}
            if not b:
                continue
            u = j["url"].split("?")[0]
            if w not in data[u]:
                data[u][w] = (j["ts"], b)
rows = []
for u, d in data.items():
    for w, (ts, b) in d.items():
        rows.append([u, w, ts, cat.get(u, ""), sum(b.values()), sum(v for k, v in b.items() if k in owned), len(b)])
with open(os.path.join(RAW, "R12_panel_facets.csv"), "w", newline="", encoding="utf-8") as fh:
    wr = csv.writer(fh); wr.writerow(["url", "window", "ts", "catgroup", "facet_sum", "owned", "n_brands"]); wr.writerows(rows)


AGG = ("markdown", "clearance", "sale", "new-arrival", "top-rated", "bazaarvoice", "-categories", "gifts", "deals",
       "last-chance", "new-search", "-new")


def compare(a, b, excl_agg=True):
    m = [u for u, d in data.items() if a in d and b in d and "x-brand" not in u
         and len(d[a][1]) >= 3 and len(d[b][1]) >= 3 and cat.get(u) != "FAN"
         and not (excl_agg and any(k in u.split("/f/")[-1] for k in AGG))]
    if not m:
        print(a, b, "no matched pages"); return
    P = lambda bb: (sum(v for k, v in bb.items() if k in owned), sum(bb.values()))
    oa = ta = ob = tb = la = lb = loa = lob = 0
    grp = defaultdict(lambda: [0, 0, 0, 0, 0])
    up = dn = 0
    for u in m:
        ba, bb = data[u][a][1], data[u][b][1]
        x, y = P(ba); z, t = P(bb)
        oa += x; ta += y; ob += z; tb += t
        common = {k for k in ba if bb.get(k)}
        la += sum(ba[k] for k in common); lb += sum(bb[k] for k in common)
        loa += sum(ba[k] for k in common if k in owned); lob += sum(bb[k] for k in common if k in owned)
        g = grp[cat.get(u, "?")]
        g[0] += x; g[1] += y; g[2] += z; g[3] += t; g[4] += 1
        if y and t:
            dlt = 100 * z / t - 100 * x / y
            up += dlt > 0.5; dn += dlt < -0.5
    print(f"\n{a} -> {b}: {len(m)} matched multi-brand category pages (page-weighted; products overlap across pages)")
    print(f"  pooled owned facet share {oa}/{ta} = {100*oa/ta:.2f}% -> {ob}/{tb} = {100*ob/tb:.2f}% ({100*ob/tb-100*oa/ta:+.2f}pts)"
          f" | like-for-like brands {100*loa/max(la,1):.2f}% -> {100*lob/max(lb,1):.2f}% | pages up {up} / down {dn}")
    import random
    random.seed(12)
    vals = [(P(data[u][a][1]), P(data[u][b][1])) for u in m]
    bs = []
    for _ in range(1000):
        s = [random.choice(vals) for _ in vals]
        A0 = sum(x[0][0] for x in s); A1 = sum(x[0][1] for x in s); B0 = sum(x[1][0] for x in s); B1 = sum(x[1][1] for x in s)
        bs.append(100 * B0 / B1 - 100 * A0 / A1)
    bs.sort()
    print(f"  bootstrap 95% CI (pages resampled) for pooled change: {bs[25]:+.2f} to {bs[974]:+.2f}pts")
    rel = [u for u in m if max(P(data[u][a][1])[0], P(data[u][b][1])[0]) > 0]
    ra = sum(P(data[u][a][1])[0] for u in rel); rta = sum(P(data[u][a][1])[1] for u in rel)
    rb = sum(P(data[u][b][1])[0] for u in rel); rtb = sum(P(data[u][b][1])[1] for u in rel)
    print(f"  pages where owned brands are present (n={len(rel)}): {100*ra/max(rta,1):.2f}% -> {100*rb/max(rtb,1):.2f}%"
          f" | owned listings {ra}->{rb} ({100*(rb/max(ra,1)-1):+.0f}%), all listings {rta}->{rtb} ({100*(rtb/max(rta,1)-1):+.0f}%)")
    ds = sorted(100 * P(data[u][b][1])[0] / P(data[u][b][1])[1] - 100 * P(data[u][a][1])[0] / P(data[u][a][1])[1] for u in rel)
    if ds:
        print(f"  per-page change (owned-present pages, equal weight): mean {sum(ds)/len(ds):+.2f}pts, median {ds[len(ds)//2]:+.2f}pts, "
              f"up {sum(1 for x in ds if x > 0.5)} / down {sum(1 for x in ds if x < -0.5)} / flat {sum(1 for x in ds if -0.5 <= x <= 0.5)}")
        big = [u for u in rel if P(data[u][a][1])[1] >= 1000]
        print(f"  pages with >=1,000 listings in {a}: {len(big)} (largest: " + ", ".join(
            f"{u.split('/f/')[1]} {P(data[u][a][1])[1]}->{P(data[u][b][1])[1]}" for u in sorted(big, key=lambda u: -P(data[u][a][1])[1])[:6]) + ")")
    from collections import Counter
    ca, cb = Counter(), Counter()
    for u in m:
        ca.update(data[u][a][1]); cb.update(data[u][b][1])
    keyb = [k for k in sorted(owned, key=lambda k: -ca[k]) if ca[k] >= 20] + ["Nike", "adidas", "Under Armour", "Jordan",
            "The North Face", "Columbia", "PUMA", "New Balance", "On", "HOKA", "Brooks", "lululemon", "Vuori", "YETI"]
    print("  brand listings (sum over matched pages): " + "; ".join(
        f"{k} {ca[k]}->{cb[k]} ({100*(cb[k]/ca[k]-1):+.0f}%)" for k in keyb if ca[k]))
    for g, x in sorted(grp.items(), key=lambda kv: -kv[1][4]):
        if x[4] >= 5:
            print(f"   {g:12s} n={x[4]:4d}  {100*x[0]/max(x[1],1):5.2f}% -> {100*x[2]/max(x[3],1):5.2f}%  ({100*x[2]/max(x[3],1)-100*x[0]/max(x[1],1):+.2f})")


print("=== excluding fan-gear and aggregator pages (markdowns/clearance/sale/new-arrivals/top-rated) ===")
compare("W25", "W26")
compare("W23", "W25")
compare("W23", "W26")
print("\n=== aggregator pages only (owned share of markdown/clearance/sale listings etc.) ===")
for u in sorted(data):
    s = u.split("/f/")[-1]
    if any(k in s for k in ("markdowns", "clearance-apparel", "clearance-apparel-gear-footwear", "sale-apparel",
                            "clothing-footwear-new-arrivals", "mens-top-rated-apparel", "womens-top-rated-apparel")):
        d = data[u]
        print("  ", s, " | ".join(f"{w} {d[w][0][:8]} {sum(v for k, v in d[w][1].items() if k in owned)}/{sum(d[w][1].values())}"
                                  f"={100*sum(v for k, v in d[w][1].items() if k in owned)/max(sum(d[w][1].values()),1):.1f}%"
                                  for w in ("W23", "W25", "W26") if w in d))
