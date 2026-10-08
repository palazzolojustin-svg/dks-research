"""V2 analysis: same definitions as X11_cc_analyze.py (owned = attr 6025 'Vertical Brand'; on_sale = displayed SKU offer<list-0.005;
depth = mean(1-offer/list) over on-sale; avg_disc = sum depth/n all products; products deduped by parent partnumber within a crawl)."""
import csv, glob, json, os, random, statistics as st, collections
CC = os.path.join(os.path.dirname(__file__), "..", "raw", "V2", "cc")
DATA = os.path.join(os.path.dirname(__file__), "..", "data")
LAB = {"CC-MAIN-2025-33": "2025-08", "CC-MAIN-2025-38": "2025-09", "CC-MAIN-2025-43": "2025-10", "CC-MAIN-2025-47": "2025-11",
       "CC-MAIN-2025-51": "2025-12", "CC-MAIN-2026-30": "2026-07", "CC-MAIN-2026-34": "2026-08", "CC-MAIN-2026-39": "2026-09",
       "WB-202510": "2025-10", "WB-202511": "2025-11", "WB-202512": "2025-12", "WB-202609": "2026-09", "WB-202610": "2026-10"}
BR = ["Nike", "adidas", "Jordan", "New Balance", "Under Armour", "Columbia", "PUMA", "The North Face", "Hoka", "Brooks"]
def f(x):
    try: return float(x)
    except Exception: return None
def load(cid):
    rows = {}
    for l in open(os.path.join(CC, cid + "_products.jsonl")):
        r = json.loads(l)
        if r["pp"] and r["pp"] not in rows: rows[r["pp"]] = r
    return list(rows.values())
def sale(r): return f(r["list"]) and f(r["offer"]) is not None and f(r["offer"]) < f(r["list"]) - 0.005
def depth(r): return 1 - f(r["offer"]) / f(r["list"]) if sale(r) else 0.0
def owned(r): return bool(r.get("vb")) and "Vertical Brand" in r["vb"]
def valid(r): return bool(f(r["list"]) and f(r["offer"]) is not None)
def M(rs):
    rs = [r for r in rs if valid(r)]; n = len(rs)
    if not n: return dict(n=0, on_sale=None, depth_on_sale=None, avg_disc=None)
    s = [r for r in rs if sale(r)]
    return dict(n=n, on_sale=len(s) / n, depth_on_sale=(sum(depth(r) for r in s) / len(s) if s else 0), avg_disc=sum(depth(r) for r in s) / n)
def pct(x): return "" if x is None else round(100 * x, 1)
def main():
    crawls = sorted({os.path.basename(p).rsplit("_", 1)[0] for p in glob.glob(os.path.join(CC, "*_products.jsonl"))})
    out = []; data = {}
    for cid in crawls:
        if cid not in LAB: continue
        rs = load(cid); data[cid] = rs
        pages = sum(1 for l in open(os.path.join(CC, cid + "_pages.jsonl")) if json.loads(l).get("has_state"))
        nat = [r for r in rs if not owned(r)]; ow = [r for r in rs if owned(r)]
        row = dict(month=LAB[cid], source="WB" if cid.startswith("WB") else "CC", crawl=cid, pages=pages, products=len(rs))
        for nm, grp in [("all", rs), ("nat", nat), ("own", ow)]:
            m = M(grp); row[nm + "_n"] = m["n"]; row[nm + "_on_sale_pct"] = pct(m["on_sale"]); row[nm + "_depth_when_on_sale_pct"] = pct(m["depth_on_sale"]); row[nm + "_avg_disc_pct"] = pct(m["avg_disc"])
        for b in BR:
            g = M([r for r in nat if r["brand"] == b]); row[b.replace(" ", "_") + "_n"] = g["n"]; row[b.replace(" ", "_") + "_on_sale_pct"] = pct(g["on_sale"])
        out.append(row)
    out.sort(key=lambda r: (r["source"], r["month"]))
    with open(os.path.join(DATA, "V2_dks_sale_share.csv"), "w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(out[0].keys())); wr.writeheader(); wr.writerows(out)
    for r in out: print({k: r[k] for k in ["month", "source", "pages", "products", "all_on_sale_pct", "nat_n", "nat_on_sale_pct", "nat_depth_when_on_sale_pct", "nat_avg_disc_pct", "all_avg_disc_pct", "own_on_sale_pct"]})
    print("brands on-sale % (n)")
    for r in out: print(r["month"], r["source"], {b: (r[b.replace(" ", "_") + "_on_sale_pct"], r[b.replace(" ", "_") + "_n"]) for b in BR[:7]})
    # y/y pooled Aug+Sep and bootstrap over pages
    def pool(cids): return [r for c in cids for r in data.get(c, [])]
    for lab, a, b in [("AugSep", ["CC-MAIN-2025-33", "CC-MAIN-2025-38"], ["CC-MAIN-2026-34", "CC-MAIN-2026-39"])]:
        for nm, flt in [("all", lambda r: True), ("national", lambda r: not owned(r)), ("owned", owned)]:
            A = [r for r in pool(a) if flt(r)]; B = [r for r in pool(b) if flt(r)]
            ma, mb = M(A), M(B)
            # bootstrap pages
            def boot(rs):
                bp = collections.defaultdict(list)
                for r in rs: bp[r["page"]].append(r)
                return bp
            ba, bb = boot(A), boot(B); rnd = random.Random(5); d = []
            for _ in range(400):
                sa = [r for p in rnd.choices(list(ba), k=len(ba)) for r in ba[p]]; sb = [r for p in rnd.choices(list(bb), k=len(bb)) for r in bb[p]]
                d.append(M(sb)["on_sale"] - M(sa)["on_sale"])
            d.sort()
            print(lab, nm, "n", ma["n"], mb["n"], "on_sale", pct(ma["on_sale"]), "->", pct(mb["on_sale"]), "depth_on_sale", pct(ma["depth_on_sale"]), "->", pct(mb["depth_on_sale"]), "avg_disc", pct(ma["avg_disc"]), "->", pct(mb["avg_disc"]), "boot90 pp", round(100 * d[20], 1), round(100 * d[380], 1))
        # matched pages (URLs captured in both years)
        pa = {r["page"].lower(): r for r in pool(a)}; 
        ua = collections.defaultdict(list); ub = collections.defaultdict(list)
        for r in pool(a): ua[r["page"].lower()].append(r)
        for r in pool(b): ub[r["page"].lower()].append(r)
        common = [u for u in ua if u in ub]
        for nm, flt in [("all", lambda r: True), ("national", lambda r: not owned(r))]:
            # page-equal-weighted mean of page on-sale share
            sa = [M([r for r in ua[u] if flt(r)])["on_sale"] for u in common]; sb = [M([r for r in ub[u] if flt(r)])["on_sale"] for u in common]
            pr = [(x, y) for x, y in zip(sa, sb) if x is not None and y is not None]
            print("matched-URL", nm, "pages", len(pr), "page-avg on_sale", pct(sum(x for x, _ in pr) / len(pr)), "->", pct(sum(y for _, y in pr) / len(pr)))
    # brand pooled y/y
    for b in BR:
        A = [r for r in pool(["CC-MAIN-2025-33", "CC-MAIN-2025-38"]) if r["brand"] == b and not owned(r)]; B = [r for r in pool(["CC-MAIN-2026-34", "CC-MAIN-2026-39"]) if r["brand"] == b and not owned(r)]
        ma, mb = M(A), M(B); print("brand", b, ma["n"], mb["n"], pct(ma["on_sale"]), "->", pct(mb["on_sale"]), "depth", pct(ma["depth_on_sale"]), "->", pct(mb["depth_on_sale"]))
    # pages-level whole-assortment Sale facet on matched Nike/UA/adidas URLs etc
    pg = {}
    for cid in data:
        for l in open(os.path.join(CC, cid + "_pages.jsonl")):
            g = json.loads(l)
            if g.get("totalCount"): pg[(cid, g["url"].lower())] = (g["totalCount"], g.get("sale_count") or 0)
    for lab, a, b in [("AugSep", ["CC-MAIN-2025-33", "CC-MAIN-2025-38"], ["CC-MAIN-2026-34", "CC-MAIN-2026-39"])]:
        ua = {}; ub = {}
        for (c, u), v in pg.items():
            if c in a: ua.setdefault(u, v)
            if c in b: ub.setdefault(u, v)
        com = [u for u in ua if u in ub]
        print("sale-facet matched pages", len(com), "sum sale/total", round(100 * sum(ua[u][1] for u in com) / sum(ua[u][0] for u in com), 1), "->", round(100 * sum(ub[u][1] for u in com) / sum(ub[u][0] for u in com), 1))
        print("sale-facet matched pages, equal-weight", round(100 * st.mean(ua[u][1] / ua[u][0] for u in com), 1), "->", round(100 * st.mean(ub[u][1] / ub[u][0] for u in com), 1))
main()
