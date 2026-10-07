"""R9: owned-brand full-price (not-on-markdown) share and realized price by brand, on the matched panel-A
URL set (same pages in W23 / W25 / W26) → a like-for-like page-set markdown series with a 2023 baseline.

Rerun: python R9_panel_price.py  → raw/R9_panel_price.csv
on sale = displayed SKU offer < list. Unique products per window (first capture of each parentPartnumber).
Also reports: share of owned products that are NEW (dsgProductSortDate within 365d of capture) per window.
"""
import collections, csv, datetime as dt, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from R9_cc_common import RAW, load_idx
from R9_panel_analyze import PANELS, load_rows, norm
from R9_cc_analyze import catgroup, is_owned, bgroup


def main():
    out = []
    P = "A"; wins = PANELS[P]
    crawls = [c for _, cs in wins for c in cs]
    urlset = set()
    for c in crawls:
        for r in load_idx(os.path.join(RAW, "R9", "idx", f"panel_{P}_{c}.jsonl")):
            urlset.add(norm(r["url"]))
    data, _ = load_rows(crawls, urlset)
    for w, cs in wins:
        U = {}
        for c in cs:
            for u, L in data[c].items():
                for r in L:
                    if catgroup(r.get("cat")) != "FAN":
                        U.setdefault(r["pp"], r)
        g = collections.defaultdict(list)
        for r in U.values():
            try:
                L_, O_ = float(r.get("list") or 0), float(r.get("offer") or 0)
            except Exception:
                continue
            if L_ > 0 and O_ > 0:
                b = bgroup(r)
                g[b].append((L_, O_))
                g["OWNED_ALL" if is_owned(r) else "NATIONAL_ALL"].append((L_, O_))
                if catgroup(r.get("cat")) in ("W_APP", "M_APP", "K_APP"):
                    g[("OWNED" if is_owned(r) else "NATL") + "_APPAREL"].append((L_, O_))
        for k, v in sorted(g.items(), key=lambda x: str(x[0])):
            if k == "NATIONAL":
                continue
            sale = [O < L - 0.005 for L, O in v]
            offers = sorted(O for _, O in v); lists = sorted(L for L, _ in v)
            out.append({"window": w, "group": k, "n": len(v), "onsale_pct": round(100 * sum(sale) / len(v), 1),
                        "fullprice_pct": round(100 - 100 * sum(sale) / len(v), 1),
                        "avg_disc_pct": round(100 * sum(max(0, 1 - O / L) for L, O in v) / len(v), 1),
                        "median_list": lists[len(lists) // 2], "median_offer": offers[len(offers) // 2]})
    with open(os.path.join(RAW, "R9_panel_price.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
    for r in out:
        print(r)


if __name__ == "__main__":
    main()
