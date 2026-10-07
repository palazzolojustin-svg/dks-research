"""R9: matched-URL panel analysis of owned-brand ('Vertical Brand') placement on dicks.com category pages.

Rerun:  python R9_panel_analyze.py
Needs:  raw/R9/idx/panel_<P>_<crawl>.jsonl (R9_panel_build.py) and the extracted captures in
        raw/R9/cc/*_products.jsonl (+ raw/X11_cc/*_products.jsonl, pooled).
Outputs: raw/R9_panel_pages.csv (one row per URL x window), raw/R9_panel_summary.csv,
         raw/R9_panel_bycat.csv, prints a summary with page-bootstrap 90% CIs.
Metrics per window, on the SAME URLs:
  owned share of all listed slots (first 48), of the first 12 slots (first rows = "first page" above
  the fold), and of slots on pages whose default sort is Top Sellers (selectedSort=1); owned share
  of unique products; owned share of Bazaarvoice review counts (R9-fetched rows only).
Page filter 'mixed': >=4 distinct brands in every window, not an owned-brand slug page, and <50% FAN
(league/college licensed) products.
"""
import collections, csv, glob, json, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from R9_cc_common import RAW, load_idx
from R9_cc_analyze import catgroup, is_owned, is_owned_page, bgroup

PANELS = {"A": [("W23", ["CC-MAIN-2023-40", "CC-MAIN-2023-50", "CC-MAIN-2024-10"]),
                ("W25", ["CC-MAIN-2025-38", "CC-MAIN-2025-33"]),
                ("W26", ["CC-MAIN-2026-39", "CC-MAIN-2026-34"])],
          "B": [("S23", ["CC-MAIN-2023-23"]), ("S26", ["CC-MAIN-2026-25", "CC-MAIN-2026-21"])],
          "G": [("G23", ["CC-MAIN-2023-40", "CC-MAIN-2023-50", "CC-MAIN-2024-10", "CC-MAIN-2023-23"]),
                ("G25", ["CC-MAIN-2025-38", "CC-MAIN-2025-33", "CC-MAIN-2025-43"]),
                ("G26", ["CC-MAIN-2026-39", "CC-MAIN-2026-34", "CC-MAIN-2026-30"])]}


OUT_SUFFIX = ""  # set by R9_run_panel.py, e.g. "_G" for the Golf Galaxy panel


def norm(u):
    return u.lower().rstrip("/")


KEEP = ("page", "pos", "pp", "brand", "vb", "cat", "rc", "list", "offer", "badge", "src", "crawl", "ts")


def slim(r):
    return {k: r.get(k) for k in KEEP}


def load_rows(crawls, urlset=None):
    data = collections.defaultdict(lambda: collections.defaultdict(list))  # crawl -> url -> rows
    sorts = {}
    for c in crawls:
        for f in glob.glob(os.path.join(RAW, "R9", "cc", f"{c}_*_products.jsonl")):
            for l in open(f, encoding="utf-8"):
                if urlset is not None:
                    i = l.find('"page": "')
                    if i >= 0:
                        j = l.find('"', i + 9)
                        if norm(l[i + 9:j]) not in urlset:
                            continue
                try:
                    r = json.loads(l)
                except Exception:
                    continue
                data[c][norm(r["page"])].append(slim(r))
        for f in glob.glob(os.path.join(RAW, "R9", "cc", f"{c}_*_pages.jsonl")):
            for l in open(f, encoding="utf-8"):
                try:
                    p = json.loads(l)
                except Exception:
                    continue
                if p.get("sort") is not None:
                    sorts[(c, norm(p["url"]))] = p["sort"]
        f = os.path.join(RAW, "X11_cc", f"{c}_products.jsonl")
        if os.path.exists(f):
            last, pos = None, 0
            for l in open(f, encoding="utf-8"):
                i = l.find('"page": "')
                j = l.find('"', i + 9)
                pg = l[i + 9:j]
                if pg != last:
                    last, pos = pg, 0
                pos += 1
                u = norm(pg)
                if urlset is not None and u not in urlset:
                    continue
                if u in data[c] and data[c][u] and data[c][u][0].get("src") != "X11":
                    continue
                try:
                    r = json.loads(l)
                except Exception:
                    continue
                r["pos"], r["src"] = pos, "X11"
                data[c][u].append(slim(r))
    # de-dup positions (a page may have been captured twice)
    for c in data:
        for u in data[c]:
            seen, out = set(), []
            for r in data[c][u]:
                k = (r.get("pos"), r.get("pp"))
                if k not in seen:
                    seen.add(k); out.append(r)
            data[c][u] = sorted(out, key=lambda r: r.get("pos") or 999)
    return data, sorts


def boot(pairs, n=2000, seed=7):
    """pairs: list of (num_a, den_a, num_b, den_b); returns pooled diff (pp) and 90% CI."""
    rnd = random.Random(seed)
    def d(P):
        na = sum(p[0] for p in P); da = sum(p[1] for p in P); nb = sum(p[2] for p in P); db = sum(p[3] for p in P)
        return 100 * (nb / db - na / da) if da and db else 0.0
    base = d(pairs)
    sims = sorted(d([pairs[rnd.randrange(len(pairs))] for _ in pairs]) for _ in range(n))
    return round(base, 2), round(sims[int(0.05 * n)], 2), round(sims[int(0.95 * n)], 2)


def main():
    out_pages, out_sum, out_cat = [], [], []
    for P, wins in PANELS.items():
        crawls = [c for _, cs in wins for c in cs]
        urlset = set()
        for c in crawls:
            for r in load_idx(os.path.join(RAW, "R9", "idx", f"panel_{P}_{c}.jsonl")):
                urlset.add(norm(r["url"]))
        data, sorts = load_rows(crawls, urlset)
        urls = None
        chosen = {}
        for w, cs in wins:
            fn = [os.path.join(RAW, "R9", "idx", f"panel_{P}_{c}.jsonl") for c in cs]
            m = {}
            for c, f in zip(cs, fn):
                for r in load_idx(f):
                    u = norm(r["url"])
                    if data[c].get(u):
                        m.setdefault(u, c)
            chosen[w] = m
            urls = set(m) if urls is None else urls & set(m)
        stats = {}
        for u in sorted(urls):
            rec = {}
            ok = not is_owned_page(u)
            for w, _ in wins:
                c = chosen[w][u]
                R = data[c][u][:48]
                fan = sum(catgroup(r.get("cat")) == "FAN" for r in R)
                nb = len({r.get("brand") for r in R})
                if nb < 4 or fan > 0.5 * len(R):
                    ok = False
                top = R[:12]
                rcR = [r for r in R if isinstance(r.get("rc"), (int, float))]
                cg = collections.Counter(catgroup(r.get("cat")) for r in R).most_common(1)[0][0]
                rec[w] = {"crawl": c, "n": len(R), "own": sum(is_owned(r) for r in R), "n12": len(top),
                          "own12": sum(is_owned(r) for r in top), "brands": nb, "sort": sorts.get((c, u)),
                          "rc": sum(r["rc"] for r in rcR), "rc_own": sum(r["rc"] for r in rcR if is_owned(r)),
                          "rc_n": len(rcR), "cg": cg, "pps": {r.get("pp"): r for r in R}}
            stats[u] = (ok, rec)
            for w, _ in wins:
                x = rec[w]
                out_pages.append({"panel": P, "url": u, "mixed": ok, "window": w, "crawl": x["crawl"], "n": x["n"],
                                  "owned": x["own"], "n12": x["n12"], "owned12": x["own12"], "brands": x["brands"],
                                  "sort": x["sort"], "catgroup": x["cg"], "rc_sum": x["rc"], "rc_owned": x["rc_own"]})
        for scope in ("all", "mixed"):
            S = [(u, rec) for u, (ok, rec) in stats.items() if scope == "all" or ok]
            if not S:
                continue
            row = {"panel": P, "scope": scope, "pages": len(S)}
            for w, _ in wins:
                n = sum(r[w]["n"] for _, r in S); o = sum(r[w]["own"] for _, r in S)
                n12 = sum(r[w]["n12"] for _, r in S); o12 = sum(r[w]["own12"] for _, r in S)
                ts = [r[w] for _, r in S if r[w]["sort"] == 1]
                uniq = {}
                for _, r in S:
                    uniq.update(r[w]["pps"])
                rcS = sum(r[w]["rc"] for _, r in S if r[w]["rc_n"]); rcO = sum(r[w]["rc_own"] for _, r in S if r[w]["rc_n"])
                row.update({f"{w}_slots": n, f"{w}_owned_pct": round(100 * o / n, 2) if n else None,
                            f"{w}_top12_owned_pct": round(100 * o12 / n12, 2) if n12 else None,
                            f"{w}_topseller_pages": len(ts),
                            f"{w}_topseller_top12_owned_pct": round(100 * sum(x["own12"] for x in ts) / sum(x["n12"] for x in ts), 2) if ts and sum(x["n12"] for x in ts) else None,
                            f"{w}_uniq": len(uniq), f"{w}_uniq_owned_pct": round(100 * sum(is_owned(r) for r in uniq.values()) / len(uniq), 2) if uniq else None,
                            f"{w}_rc_pages": sum(1 for _, r in S if r[w]["rc_n"]),
                            f"{w}_rc_owned_pct": round(100 * rcO / rcS, 2) if rcS else None})
            ws = [w for w, _ in wins]
            for a, b in zip(ws, ws[1:]) if len(ws) > 1 else []:
                row[f"d_{a}_{b}_slots_pp"] = boot([(r[a]["own"], r[a]["n"], r[b]["own"], r[b]["n"]) for _, r in S])
                row[f"d_{a}_{b}_top12_pp"] = boot([(r[a]["own12"], r[a]["n12"], r[b]["own12"], r[b]["n12"]) for _, r in S])
            if len(ws) == 3:
                a, b = ws[0], ws[2]
                row[f"d_{a}_{b}_slots_pp"] = boot([(r[a]["own"], r[a]["n"], r[b]["own"], r[b]["n"]) for _, r in S])
                row[f"d_{a}_{b}_top12_pp"] = boot([(r[a]["own12"], r[a]["n12"], r[b]["own12"], r[b]["n12"]) for _, r in S])
            # page-level direction counts (first vs last window)
            a, b = ws[0], ws[-1]
            up = sum(1 for _, r in S if r[b]["n"] and r[a]["n"] and r[b]["own"] / r[b]["n"] > r[a]["own"] / r[a]["n"])
            dn = sum(1 for _, r in S if r[b]["n"] and r[a]["n"] and r[b]["own"] / r[b]["n"] < r[a]["own"] / r[a]["n"])
            row["pages_up_first_to_last"], row["pages_down_first_to_last"] = up, dn
            out_sum.append(row)
            print(json.dumps(row))
            # by category group (page modal catgroup in last window)
            cg = collections.defaultdict(list)
            for u, r in S:
                cg[r[ws[-1]]["cg"]].append(r)
            for k, L in sorted(cg.items()):
                rr = {"panel": P, "scope": scope, "catgroup": k, "pages": len(L)}
                for w in ws:
                    n = sum(x[w]["n"] for x in L); o = sum(x[w]["own"] for x in L)
                    n12 = sum(x[w]["n12"] for x in L); o12 = sum(x[w]["own12"] for x in L)
                    rr[f"{w}_owned_pct"] = round(100 * o / n, 2) if n else None
                    rr[f"{w}_top12_owned_pct"] = round(100 * o12 / n12, 2) if n12 else None
                out_cat.append(rr)
    for name, data in (("R9_panel_pages.csv", out_pages), ("R9_panel_summary.csv", out_sum), ("R9_panel_bycat.csv", out_cat)):
        name = name.replace(".csv", OUT_SUFFIX + ".csv")
        if data:
            keys = []
            for d in data:
                for k in d:
                    if k not in keys:
                        keys.append(k)
            with open(os.path.join(RAW, name), "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(data)


if __name__ == "__main__":
    main()
