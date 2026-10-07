"""R1 (wave 4): increment sweep on the unchanged B7/R1 engine (imports scripts\\R1_thesis1_model.py).

Rerun:  python THESIS_SCRAPE\\scripts\\R1_sweep.py   (from C:\\Users\\palaz\\Downloads\\DKS_RESEARCH)
Writes: THESIS_SCRAPE\\raw\\R1_increment_sweep.csv ; prints tables.
For each HoS relocation increment ($0-25M; other inputs = R1 base) it reports, for 2H FY26 and FY27:
consensus-implied legacy comp, trailing-8Q legacy (same engine), deceleration, variance at the base evidence legacy
(1.5% 2H26 / 2.25% FY27), revenue $M and bps, EPS at 20%, and the B8 check (engine FY24 format wedge incl. GameChanger).
"""
import os, sys, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import R1_thesis1_model as M

def period(rows, qs, idx):
    rr = [r for r in rows if r["q"] in qs]
    w = sum(r["base"] for r in rr)
    return sum(r[idx] * r["base"] for r in rr) / w

def evaluate(p, leg26=1.5, leg27=2.25):
    hist = M.run(M.HIST, p)
    bt = [M.implied_legacy(M.ACTUAL_COMP[q], hist[q], p, M.HIST_ONEOFF.get(q, 0.0)) for q in M.BT]
    trail = sum(bt[-8:]) / 8
    fy24_wedge = sum(hist[q]["F"] - hist[q]["K"] for q in M.BT[:4]) / 4 + M.GC
    rc = M.run(M.HIST + M.cons_path(p["relo27"]), p)
    re_ = M.run(M.HIST + M.EVID, p)
    rows = []
    for q in M.FWD:
        lap = p["laps"].get(q, 0.0)
        il = M.implied_legacy(M.CONS_COMP[q], rc[q], p, lap)
        leg = leg26 if q.startswith("FY26") else leg27
        mc = leg + re_[q]["w_m"] * p["mature_diff"] + re_[q]["F"] - re_[q]["K"] + M.GC + lap
        trev = (mc - M.CONS_COMP[q]) / 100 * rc[q]["base"] + re_[q]["NEW"] - rc[q]["NEW"]
        rows.append(dict(q=q, il=il, var=mc - M.CONS_COMP[q], trev=trev, base=rc[q]["base"]))
    out = {"trail": trail, "fy24_wedge": fy24_wedge}
    for name, qs, den in (("2H26", M.FWD[:2], 7457.2), ("FY27", M.FWD[2:], 15203.0)):
        il = period(rows, qs, "il"); var = period(rows, qs, "var")
        trev = sum(r["trev"] for r in rows if r["q"] in qs)
        out[name] = dict(il=il, decel=trail - il, var=var, rev=trev, bps=trev / den * 1e4,
                         eps=trev * 0.20 * (1 - M.TAX) / M.SH)
    return out

def main():
    base = dict(M.SCEN["base"])
    out = []
    print("inc $M | FY24 wedge (B8: 0.6 mean / 1.3 median, s.e. 1.45) | trailing legacy | 2H26: implied legacy, decel, var pts, $M, bps, EPS | FY27: implied, decel, var, $M, bps, EPS")
    for inc in (0, 4, 6, 7, 8, 10, 12, 14, 16, 20, 25):
        p = dict(base); p["hos_inc"] = float(inc)
        r = evaluate(p)
        a, b = r["2H26"], r["FY27"]
        out.append([inc, round(r["fy24_wedge"], 2), round(r["trail"], 2)] +
                   [round(a[k], 2) for k in ("il", "decel", "var", "rev", "bps", "eps")] +
                   [round(b[k], 2) for k in ("il", "decel", "var", "rev", "bps", "eps")])
        print(f"{inc:5.0f} | {r['fy24_wedge']:.2f} | {r['trail']:+.2f} | {a['il']:+.2f} {a['decel']:.2f} {a['var']:+.2f} {a['rev']:+.0f} {a['bps']:+.0f}bp "
              f"{a['eps']:+.3f} | {b['il']:+.2f} {b['decel']:.2f} {b['var']:+.2f} {b['rev']:+.0f} {b['bps']:+.0f}bp {b['eps']:+.3f}")
    # breakeven legacy = implied legacy; also EPS per 1pt of legacy
    print("\n2H26 variance at base increment ($12M) for alternative evidence-legacy anchors:")
    p = dict(base)
    for leg, lab in ((0.38, "= consensus-implied (breakeven)"), (1.0, "mgmt-guide-like"), (1.5, "B7/R1 base"),
                     (2.0, "D06 alt-data total ~3.25% minus R1 format ~0.96 minus GC 0.3"), (2.5, "B8: trailing reported 4.99% minus 1.3pt wedge, minus 1.2pt decel"),
                     (3.75, "trailing 8Q (no slowdown)")):
        r = evaluate(p, leg26=leg)["2H26"]
        print(f"  legacy {leg:4.2f}% ({lab}): var {r['var']:+.2f}pt, {r['rev']:+.0f}M, {r['bps']:+.0f}bp, EPS {r['eps']:+.3f}")
    print("\n2H26 variance at LOW increment ($7M) for alternative anchors:")
    p = dict(base); p["hos_inc"] = 7.0
    for leg in (0.79, 1.0, 1.5, 2.0, 2.5):
        r = evaluate(p, leg26=leg)["2H26"]
        print(f"  legacy {leg:4.2f}%: var {r['var']:+.2f}pt, {r['rev']:+.0f}M, {r['bps']:+.0f}bp, EPS {r['eps']:+.3f}")
    print("\nFY27 at base increment for legacy 1.5-3.0:")
    p = dict(base)
    for leg in (1.5, 2.0, 2.25, 2.5, 3.0):
        r = evaluate(p, leg27=leg)["FY27"]
        print(f"  legacy {leg:4.2f}%: var {r['var']:+.2f}pt, {r['rev']:+.0f}M, {r['bps']:+.0f}bp, EPS {r['eps']:+.3f}")
    with open(os.path.join(M.RAW, "R1_increment_sweep.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["hos_inc_$M", "fy24_engine_wedge_pts", "trailing_8Q_legacy",
                    "2H26_implied_legacy", "2H26_decel", "2H26_var_pts", "2H26_rev_$M", "2H26_bps", "2H26_eps20",
                    "FY27_implied_legacy", "FY27_decel", "FY27_var_pts", "FY27_rev_$M", "FY27_bps", "FY27_eps20"])
        w.writerows(out)

if __name__ == "__main__":
    main()
