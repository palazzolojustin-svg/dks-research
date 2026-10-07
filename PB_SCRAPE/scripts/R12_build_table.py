"""R12: build the category x period table of owned-brand share of listed products (brand-facet based) and the
weighted all-category y/y change.

Inputs (all produced without touching dicks.com live):
  raw/R12_wb_plp.csv        Wayback captures (R12_wayback_plp.py)
  raw/R12_cc_plp.csv        Common Crawl captures (R12_cc_plp.py)
  raw/X02_wb_cache/*.html   X02's cached Wayback pages (re-parsed with the 2-layout parser)
  raw/X02_dsg_brandfacets_20261007.json, raw/X02_gg_brandfacets_20261007.json   live census 2026-10-07 (X02, browser)
Outputs:
  raw/R12_obs_long.csv        every observation (source, host, slug, date, period, total, owned, owned_pct, first24)
  raw/R12_category_table.csv  category x period (one obs per period: the one nearest the period's target date)
  printed summary: matched y/y comparisons + pooled / median deltas
Rerun: python PB_SCRAPE\\scripts\\R12_build_table.py
Owned = brands DKS itself flags with attribute 6025 'Vertical Brand' (OWNED_BASE + any brand flagged in any parsed page).
"""
import csv, glob, json, os, sys
from datetime import datetime, date
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from R12_common import RAW, parse_plp, OWNED_BASE
from R12_wayback_plp import DKS, GG

PERIODS = [  # name, start, end, target
    ("22H1", "20220101", "20220630", "20220415"), ("22H2", "20220701", "20221231", "20221015"),
    ("23H1", "20230101", "20230630", "20230415"), ("23H2", "20230701", "20240131", "20231015"),
    ("24A", "20240201", "20240531", "20240415"), ("24B", "20240601", "20241031", "20240820"),
    ("25A", "20250201", "20250630", "20250415"), ("25B", "20250701", "20251031", "20250825"),
    ("25C", "20251101", "20260131", "20251215"), ("26A", "20260201", "20260630", "20260415"),
    ("26B", "20260701", "20261006", "20260825"), ("LIVE", "20261007", "20261007", "20261007")]


GROUP = {}
for g, ss in {"w_apparel": "womens-athletic-leggings sports-bras shop-womens-joggers womens-shorts-1 womens-jackets-vests womens-shirts-tops",
              "m_apparel": "mens-shirts mens-shorts mens-pants mens-joggers",
              "k_apparel": "girls-leggings girls-shirts-tops boys-shirts-tops boys-shorts",
              "golf_apparel": "mens-golf-apparel womens-golf-apparel golf-clothes-apparel-for-men womens-golf-clothes-and-apparel",
              "golf_hard": "golf-balls golf-clubs golf-drivers putters golf-wedges golf-bags-accessories-1 golf-gloves golf-ball-dozens shop-drivers golf-irons-sets",
              "footwear": "mens-running-shoes womens-running-shoes",
              "team": "baseball-bats baseball-gloves all-soccer-balls basketballs",
              "outdoor": "camping-family-tents sleeping-bags camping-coolers backpacks-duffle-bags water-bottles-hydration bikes",
              "fitness": "dumbbells weight-benches strength-training-equipment treadmills yoga-mats"}.items():
    for s in ss.split():
        GROUP[s] = g


def period(d8):
    for n, a, b, t in PERIODS:
        if a <= d8 <= b:
            return n
    return None


def load():
    obs = []
    flagged = set()
    for fn, src in [(os.path.join(RAW, "R12_wb_plp.csv"), "wayback"), (os.path.join(RAW, "R12_cc_plp.csv"), "cc"),
                    (os.path.join(RAW, "R12_x03_harvest.csv"), "wayback(X03 cache)")]:
        if not os.path.exists(fn):
            continue
        for r in csv.DictReader(open(fn, encoding="utf-8")):
            if r["variant"] != "default":
                continue
            flagged |= set(x for x in r["flagged_brands"].split("|") if x)
            obs.append(dict(src=src, host=r["host"], slug=r["slug"], d8=r["ts"][:8], total=r["total"],
                            brands=json.loads(r["brands_json"]), first24=r["first24_own"], first24n=r["first24_n"],
                            sort=r["sort"], store=r["store"]))
    seen = {(o["host"], o["slug"], o["d8"]) for o in obs}
    for f in glob.glob(os.path.join(RAW, "X02_wb_cache", "plp_*.html")):
        b = os.path.basename(f)[4:-5]
        slug, ts = b.rsplit("_", 1)
        if ("dks", slug, ts[:8]) in seen:
            continue
        p = parse_plp(open(f, encoding="utf-8", errors="replace").read())
        if p:
            flagged |= {x[1] for x in p["products"] if x[2]}
            obs.append(dict(src="wayback(X02 cache)", host="dks", slug=slug, d8=ts[:8], total=p["total"],
                            brands=p["brands"], first24=sum(x[2] for x in p["products"][:24]),
                            first24n=min(24, len(p["products"])), sort=p["sort"], store=p["store"]))
    for host, fn in [("dks", "X02_dsg_brandfacets_20261007.json"), ("gg", "X02_gg_brandfacets_20261007.json")]:
        fp = os.path.join(RAW, fn)
        if not os.path.exists(fp):
            continue
        j = json.load(open(fp, encoding="utf-8"))
        for slug, v in j.items():
            if not isinstance(v, dict) or "brands" not in v:
                continue
            obs.append(dict(src="live census (X02)", host=host, slug=slug, d8="20261007", total=v.get("total"),
                            brands=v["brands"], first24="", first24n="", sort="", store=""))
    owned = OWNED_BASE | flagged
    for o in obs:
        b = {k: int(v) for k, v in o["brands"].items() if v is not None}
        o["facet_sum"] = sum(b.values())
        o["owned"] = sum(v for k, v in b.items() if k in owned)
        o["owned_pct"] = round(100 * o["owned"] / o["facet_sum"], 2) if o["facet_sum"] else None
        o["period"] = period(o["d8"])
        o["owned_brands"] = "; ".join(f"{k} {v}" for k, v in sorted(b.items(), key=lambda kv: -kv[1]) if k in owned)
    return obs, owned, flagged


def main():
    global OWNED_ALL
    obs, owned, flagged = load()
    OWNED_ALL = owned
    obs = [o for o in obs if o["facet_sum"]]
    cols = ["src", "host", "slug", "d8", "period", "total", "facet_sum", "owned", "owned_pct", "first24", "first24n",
            "sort", "store", "owned_brands"]
    with open(os.path.join(RAW, "R12_obs_long.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, cols, extrasaction="ignore")
        w.writeheader()
        for o in sorted(obs, key=lambda o: (o["host"], o["slug"], o["d8"])):
            w.writerow(o)
    # one obs per (host, slug, period): nearest target
    tgt = {n: datetime.strptime(t, "%Y%m%d") for n, a, b, t in PERIODS}
    cell = {}
    for o in obs:
        if not o["period"]:
            continue
        k = (o["host"], o["slug"], o["period"])
        dist = abs((datetime.strptime(o["d8"], "%Y%m%d") - tgt[o["period"]]).days)
        if k not in cell or dist < cell[k][0]:
            cell[k] = (dist, o)
    pn = [p[0] for p in PERIODS]
    slugs = [("dks", s) for s in DKS] + [("gg", s) for s in GG]
    with open(os.path.join(RAW, "R12_category_table.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["host", "slug"] + [f"{p}_{x}" for p in pn for x in ("date", "owned", "total", "pct")])
        for h, s in slugs:
            row = [h, s]
            for p in pn:
                o = cell.get((h, s, p), (None, None))[1]
                row += [o["d8"], o["owned"], o["facet_sum"], o["owned_pct"]] if o else ["", "", "", ""]
            w.writerow(row)
    print("owned set used:", sorted(owned))
    print("brands flagged 6025 in archived pages:", sorted(flagged))
    # comparisons
    def comp(a_list, b, label):
        rows = []
        for h, s in slugs:
            oa = None
            for a in a_list:
                if (h, s, a) in cell:
                    oa = cell[(h, s, a)][1]
                    break
            ob = cell.get((h, s, b), (None, None))[1]
            if oa and ob:
                rows.append((h, s, oa, ob))
        if not rows:
            print(f"\n{label}: no matched categories")
            return rows
        so_a = sum(r[2]["owned"] for r in rows); st_a = sum(r[2]["facet_sum"] for r in rows)
        so_b = sum(r[3]["owned"] for r in rows); st_b = sum(r[3]["facet_sum"] for r in rows)
        d = sorted(r[3]["owned_pct"] - r[2]["owned_pct"] for r in rows)
        med = d[len(d) // 2] if len(d) % 2 else (d[len(d) // 2 - 1] + d[len(d) // 2]) / 2
        up = sum(1 for x in d if x > 0.5); dn = sum(1 for x in d if x < -0.5)
        # owned-relevant categories (owned >=5% in either period)
        rel = [r for r in rows if max(r[2]["owned_pct"], r[3]["owned_pct"]) >= 5]
        ro_a = sum(r[2]["owned"] for r in rel); rt_a = sum(r[2]["facet_sum"] for r in rel)
        ro_b = sum(r[3]["owned"] for r in rel); rt_b = sum(r[3]["facet_sum"] for r in rel)
        print(f"\n{label}: n={len(rows)} matched | pooled {so_a}/{st_a}={100*so_a/st_a:.1f}% -> {so_b}/{st_b}={100*so_b/st_b:.1f}% "
              f"({100*so_b/st_b-100*so_a/st_a:+.1f}pts) | median cat delta {med:+.1f}pts | up {up} / down {dn} / flat {len(d)-up-dn}"
              f" | owned-relevant (>=5%) n={len(rel)}: {100*ro_a/max(rt_a,1):.1f}% -> {100*ro_b/max(rt_b,1):.1f}% | "
              f"owned count {so_a}->{so_b} ({100*(so_b/max(so_a,1)-1):+.0f}%), total {st_a}->{st_b} ({100*(st_b/max(st_a,1)-1):+.0f}%)")
        # group-level pooled shares + apparel/hardlines 50:50 composite (ex footwear) + equal-weight mean delta
        gs = {}
        for h, s, oa, ob in rows:
            g = GROUP.get(s, "other")
            x = gs.setdefault(g, [0, 0, 0, 0, 0])
            x[0] += oa["owned"]; x[1] += oa["facet_sum"]; x[2] += ob["owned"]; x[3] += ob["facet_sum"]; x[4] += 1
        line = []
        comp_ = {"apparel": [0, 0, 0, 0], "hardlines": [0, 0, 0, 0]}
        for g, x in sorted(gs.items()):
            line.append(f"{g}(n={x[4]}) {100*x[0]/max(x[1],1):.1f}->{100*x[2]/max(x[3],1):.1f}")
            k = "apparel" if "apparel" in g else ("hardlines" if g != "footwear" else None)
            if k:
                for i in range(4):
                    comp_[k][i] += x[i]
        print("   groups: " + " | ".join(line))
        # like-for-like brand set: only brands listed in BOTH periods in that category (removes drop-ship/3P brand churn)
        la = lb = loa = lob = 0
        for h, s, oa, ob in rows:
            ba = {k: int(v) for k, v in oa["brands"].items()}
            bb = {k: int(v) for k, v in ob["brands"].items()}
            common = {k for k in ba if ba[k] > 0 and bb.get(k, 0) > 0}
            la += sum(ba[k] for k in common); lb += sum(bb[k] for k in common)
            loa += sum(ba[k] for k in common if k in OWNED_ALL); lob += sum(bb[k] for k in common if k in OWNED_ALL)
        print(f"   like-for-like brands only: {loa}/{la}={100*loa/max(la,1):.1f}% -> {lob}/{lb}={100*lob/max(lb,1):.1f}% "
              f"({100*lob/max(lb,1)-100*loa/max(la,1):+.1f}pts)")
        if all(v[1] and v[3] for v in comp_.values()):
            a0 = 0.5 * comp_["apparel"][0] / comp_["apparel"][1] + 0.5 * comp_["hardlines"][0] / comp_["hardlines"][1]
            a1 = 0.5 * comp_["apparel"][2] / comp_["apparel"][3] + 0.5 * comp_["hardlines"][2] / comp_["hardlines"][3]
            print(f"   50:50 apparel/hardlines composite (ex footwear): {100*a0:.2f}% -> {100*a1:.2f}% ({100*(a1-a0):+.2f}pts; relative {100*(a1/a0-1):+.0f}%)"
                  f" | equal-weight mean category delta {sum(d)/len(d):+.2f}pts")
        for h, s, oa, ob in sorted(rows, key=lambda r: r[3]["owned_pct"] - r[2]["owned_pct"]):
            print(f"   {h}:{s:32s} {oa['d8']} {oa['owned']:>4}/{oa['facet_sum']:<5} {oa['owned_pct']:5.1f}%  ->  {ob['d8']} "
                  f"{ob['owned']:>4}/{ob['facet_sum']:<5} {ob['owned_pct']:5.1f}%  {ob['owned_pct']-oa['owned_pct']:+5.1f}  [{oa['src']} -> {ob['src']}]")
        return rows
    comp(["25B"], "LIVE", "Aug/Sep-2025 (25B) -> live 2026-10-07")
    comp(["25B"], "26B", "Aug/Sep-2025 (25B) -> Jul-Sep 2026 (26B), same season, same archive sources")
    comp(["24A"], "25B", "Feb-May 2024 (24A) -> Aug/Sep-2025 (25B)")
    comp(["24A"], "26A", "Feb-May 2024 (24A) -> Feb-Jun 2026 (26A), same season 2-yr")
    comp(["24A", "23H2"], "LIVE", "Early-2024 (24A, else 23H2) -> live 2026-10-07 (2.5-yr)")
    comp(["23H1"], "26A", "H1-2023 -> H1-2026 (3-yr, same season)")
    comp(["25A"], "26A", "Feb-Jun 2025 (25A) -> Feb-Jun 2026 (26A)")
    comp(["25C"], "26B", "Nov25-Jan26 (25C) -> Jul-Sep26")


if __name__ == "__main__":
    main()
