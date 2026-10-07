"""R9: Bazaarvoice review-count VELOCITY from Common Crawl listing snapshots (independent cross-check of X01).

For every product (parentPartnumber) seen in two captures (earliest in window A, latest in window B),
new reviews = rc_B - rc_A (floored at 0). Owned share of new reviews = owned delta / total delta.
Pairs: W23 (Sep-23..Mar-24) -> W25 (Aug-Sep-25) and W25 -> W26 (Aug-Sep-26); also crawl-to-crawl
within 2023 (2023-40 -> 2024-10). FanShop excluded. Survivorship: products must be listed in both
windows, so this measures review flow on continuing products only.
Rerun: python R9_rc_velocity.py → raw/R9_rc_velocity.csv
"""
import collections, csv, datetime as dt, glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from R9_cc_common import RAW
from R9_cc_analyze import catgroup, is_owned, bgroup

HOST = sys.argv[1] if len(sys.argv) > 1 else "dks"   # dks | gg | pl   (python R9_rc_velocity.py gg)
WINDOWS = {"W23": ["CC-MAIN-2023-40", "CC-MAIN-2023-50", "CC-MAIN-2024-10"], "W25": ["CC-MAIN-2025-33", "CC-MAIN-2025-38"],
           "W26": ["CC-MAIN-2026-34", "CC-MAIN-2026-39"], "S23": ["CC-MAIN-2023-23"], "S26": ["CC-MAIN-2026-21", "CC-MAIN-2026-25"],
           "J26": ["CC-MAIN-2026-04"]}


def load():
    obs = collections.defaultdict(dict)  # pp -> {(ts): (rc, row)}
    for f in glob.glob(os.path.join(RAW, "R9", "cc", "*_products.jsonl")):
        for l in open(f, encoding="utf-8"):
            try:
                r = json.loads(l)
            except Exception:
                continue
            if not isinstance(r.get("rc"), (int, float)) or not r.get("pp"):
                continue
            if catgroup(r.get("cat")) == "FAN":
                continue
            h = "gg" if "golfgalaxy" in r["page"] else ("pl" if "publiclands" in r["page"] else "dks")
            if h != HOST:
                continue
            obs[r["pp"]][r["ts"]] = (r["rc"], r)
    return obs


def main():
    obs = load()
    rows = []
    for a, b in (("W23", "W25"), ("W25", "W26"), ("W23", "W26"), ("S23", "S26"), ("J26", "W26")):
        ca, cb = set(WINDOWS[a]), set(WINDOWS[b])
        agg = collections.defaultdict(lambda: [0, 0.0, 0])  # group -> [n, delta, rc_a]
        for pp, d in obs.items():
            A = sorted((ts, v) for ts, v in d.items() if v[1]["crawl"] in ca)
            B = sorted((ts, v) for ts, v in d.items() if v[1]["crawl"] in cb)
            if not A or not B:
                continue
            ta, (rca, ra) = A[0]; tb, (rcb, rb) = B[-1]
            days = (dt.date(int(tb[:4]), int(tb[4:6]), int(tb[6:8])) - dt.date(int(ta[:4]), int(ta[4:6]), int(ta[6:8]))).days
            if days <= 0:
                continue
            delta = max(0, rcb - rca) * 365.0 / days  # annualised
            for g in ("ALL", "OWNED" if is_owned(rb) else "NATIONAL", "B_" + bgroup(rb), "C_" + catgroup(rb.get("cat")) + ("_O" if is_owned(rb) else "_N")):
                agg[g][0] += 1; agg[g][1] += delta; agg[g][2] += rca
        tot = agg["ALL"][1]
        for g, (n, dlt, rca) in sorted(agg.items()):
            rows.append({"pair": f"{a}->{b}", "group": g, "products": n, "annualised_new_reviews": round(dlt, 1),
                         "share_of_new_reviews_pct": round(100 * dlt / tot, 2) if tot else None,
                         "rc_at_start": rca, "share_of_start_stock_pct": round(100 * rca / agg["ALL"][2], 2) if agg["ALL"][2] else None,
                         "new_per_product": round(dlt / n, 2) if n else None})
    with open(os.path.join(RAW, "R9_rc_velocity.csv" if HOST == "dks" else f"R9_{HOST}_rc_velocity.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    for r in rows:
        if r["group"] in ("ALL", "OWNED", "NATIONAL") or r["group"].startswith("B_"):
            print(r)


if __name__ == "__main__":
    main()
