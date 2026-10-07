"""A1 robustness: widen the Academy apparel basket with /c/shops/state-pride, /c/browse/apparel and
/c/shops/workwear-clothing-boots categories (where Magellan state-graphic tees and workwear sit), pull their reviews,
and recompute owned share for the broad basket (core apparel + extra). Footwear/boot-named products are dropped.
Outputs raw/A1_academy_products_extra.csv, raw/A1_academy_reviews_extra.csv ; prints Apr-Aug / Feb-Jul shares.
RERUN: python A1_robust_broad.py
"""
import csv, os, re, sys, collections
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(__file__))
from A1_bv_academy_common import session, get, RAW
from A1_analyze import OWNED_RE, variant_of, load

EXTRA = re.compile(r"/c/(shops/state-pride|browse/apparel|shops/workwear-clothing-boots)", re.I)
FOOT = re.compile(r"\b(shoes?|cleats?|slides?|sandals?|boots?|sneakers?|clogs?|flip[- ]?flops?|slippers?)\b", re.I)


def main():
    s = session()
    core = {r["product_id"] for r in csv.DictReader(open(os.path.join(RAW, "A1_academy_products_apparel.csv"), encoding="utf-8"))}
    cats = [r for r in csv.DictReader(open(os.path.join(RAW, "A1_academy_categories.csv"), encoding="utf-8")) if EXTRA.search(r["url"] or "")]
    print("extra cats", len(cats))
    prods = {}

    def pull(c):
        flt = [("Filter", "TotalReviewCount:gte:1"), ("Filter", f"CategoryAncestorId:eq:{c['id']}")]
        n = get(s, "products", flt + [("Limit", "1")]).get("TotalResults") or 0
        out = []
        for o in range(0, n, 100):
            out += get(s, "products", flt + [("Stats", "Reviews"), ("Limit", "100"), ("Offset", str(o))]).get("Results", [])
        return out
    with ThreadPoolExecutor(6) as ex:
        for res in ex.map(pull, cats):
            for x in res:
                st = x.get("ReviewStatistics") or {}
                if x["Id"] in core or FOOT.search(x.get("Name") or "") or (st.get("LastSubmissionTime") or "")[:10] < "2023-01-01":
                    continue
                prods[x["Id"]] = [x["Id"], (x.get("Brand") or {}).get("Name"), x.get("Name")]
    print("extra products", len(prods))
    with open(os.path.join(RAW, "A1_academy_products_extra.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["product_id", "brand_name", "name"]); w.writerows(prods.values())

    def revs(pid):
        rows, off = [], 0
        while True:
            r = get(s, "reviews", [("Filter", f"ProductId:eq:{pid}"), ("Filter", "SubmissionTime:gte:1672531200"),
                                   ("Filter", "IsSyndicated:eq:false"), ("Limit", "100"), ("Offset", str(off))])
            res = r.get("Results", [])
            rows += [(x.get("Id"), pid, x.get("SubmissionTime"), x.get("CampaignId") or "") for x in res]
            off += 100
            if r.get("TotalResults") is None or off >= r["TotalResults"] or not res:
                return rows
    allr = []
    with ThreadPoolExecutor(8) as ex:
        for rr in ex.map(revs, list(prods)):
            allr += rr
    with open(os.path.join(RAW, "A1_academy_reviews_extra.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["review_id", "product_id", "submission_time", "campaign_id"]); w.writerows(allr)
    extra = []
    seen = set()
    for rid, pid, t, c in allr:
        if rid in seen: continue
        seen.add(rid)
        bn = (prods[pid][1] or "").replace("\x99", "").replace("™", "").replace("®", "").strip()
        extra.append({"y": int(t[:4]), "m": int(t[5:7]), "owned": bool(OWNED_RE.match(bn)), "vars": variant_of(c), "brand": bn})
    core_rows = load()
    for name, rows in (("EXTRA only", extra), ("BROAD (core+extra)", core_rows + extra)):
        for win, ms in (("Apr-Aug", range(4, 9)), ("Feb-Jul", range(2, 8))):
            for v in ("ALLX", "EMAIL"):
                line = []
                for y in (2023, 2024, 2025, 2026):
                    sub = [r for r in rows if v in r["vars"] and r["y"] == y and r["m"] in ms]
                    if sub:
                        line.append(f"{y}:{sum(r['owned'] for r in sub) / len(sub) * 100:.1f}(n={len(sub)})")
                print(name, win, v, "  ".join(line), flush=True)


if __name__ == "__main__":
    main()
