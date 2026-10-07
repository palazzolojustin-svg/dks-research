"""F2 (wave 1): quarter-by-quarter House of Sport / Field House comp contribution and sales-per-sq-ft math.

Rerun:  python THESIS_SCRAPE\\scripts\\F2_format_comp_math.py   (from C:\\Users\\palaz\\Downloads\\DKS_RESEARCH)
Writes: THESIS_SCRAPE\\raw\\F2_format_comp_schedule.csv and F2_sqft_productivity.csv, prints summary tables.

Inputs (all from CORE_NOTES\\C01_SYNTHESIS_B.md, PR synthesis section 1A/1B store tables + IS tables, unless noted):
- HoS store counts by quarter end: Q4FY23 12, Q1FY24 14, Q2FY24 14, Q3FY24 17, Q4FY24 19, Q1FY25 21, Q2FY25 22,
  Q3FY25 35, Q4FY25 35, Q1FY26 36, Q2FY26 41.  FH: Q3FY24 22, Q4FY24 27 (restated), Q1FY25 31, Q2FY25 35, Q3FY25 41,
  Q4FY25 42, Q1FY26 44, Q2FY26 52.  FY24 FH openings 15 (FYE23 base 12 restated) -> Q1-Q3FY24 split 3/4/4 ASSUMED.
- Plans/consensus: FY26 ~14 HoS / ~20 FH (Aug-26); BBG cons HoS 49 FY26E, 68-69 FY27E; FH 63 / 81 (KNOWN_BRIEF).
  2H FY26 split ASSUMED Q3 7 HoS + 8 FH, Q4 1 HoS + 2 FH (pre-opening peaks Q3; cons Q3 pre-open $33.8M = series high).
  FY27 18 HoS ASSUMED 2/4/10/2; ~19 FH ASSUMED 4/5/8/2.
- Relocation share (rest are new stores, which are NOT in comp for 14 months): FY24 HoS 6 of 7, FH 11 of 15
  (DKS_PRIMER: "only 1 of 7 HoS and 4 of 15 FH net-new"); FY25 HoS 13 of 16, FH 13 of 15 (F1-R2, FY25 10-K store table);
  FY26-27 75% (FY25 10-K: ~75% of FY26 openings relocations/remodels).
- Incremental annual sales per relocation: HoS $20M base ($35M yr-1 omni vs ~$15M displaced store, UBS 2026-03-02);
  FH $2.5M base (Wells FH $14M at 119% of DSG B&M productivity vs ~$11.5-12.5M legacy box) -> calibrated so FY24/FY25
  totals land near Wells' disaggregation (relocations +2.2 / +2.3 pts).
- Timing: opening assumed mid-quarter: weight 0.5 in opening quarter, 1.0 next three quarters, 0.5 in the anniversary
  quarter (after 12 months the relocated store comps against its own new-format base).  Year-2 "modestly positive"
  comping-the-comp effect ignored (conservative).
- Seasonality: incremental sales spread by FY25 DICK'S quarterly sales mix (22.5/25.8/22.9/28.7%).
- GameChanger comp contribution 0.3 pt/qtr (Wells FY26-28E).
- Reported DICK'S comps; consensus DICK'S comps 3Q26E 1.69, 4Q26E 1.59, 1Q27E 2.41, 2Q27E 2.24 (KNOWN_BRIEF/BBG).
All outputs are INFERENCE (model), not company disclosure.
"""
import csv, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "raw")
os.makedirs(RAW, exist_ok=True)

Q = ["Q1FY24","Q2FY24","Q3FY24","Q4FY24","Q1FY25","Q2FY25","Q3FY25","Q4FY25",
     "Q1FY26","Q2FY26","Q3FY26E","Q4FY26E","Q1FY27E","Q2FY27E","Q3FY27E","Q4FY27E"]
hos_open = [2,0,3,2, 2,1,13,0, 1,5,7,1, 2,4,10,2]
fh_open  = [3,4,4,4, 4,4,6,1, 2,8,8,2, 4,5,8,2]
def reloc_share(q, fmt):
    fy = q[2:6]
    if fy == "FY24": return 6/7 if fmt == "H" else 11/15
    if fy == "FY25": return 13/16 if fmt == "H" else 13/15
    return 0.75
# DICK'S segment net sales $M (prior-year base). Q4FY23 13-wk adjusted. Q3/Q4 FY26E from cons (derived in C01B 6.4 / KNOWN).
sales = {"Q1FY23":2842.2,"Q2FY23":3223.6,"Q3FY23":3042.4,"Q4FY23":3705.9,
         "Q1FY24":3018.4,"Q2FY24":3473.6,"Q3FY24":3057.2,"Q4FY24":3893.6,
         "Q1FY25":3174.7,"Q2FY25":3646.6,"Q3FY25":3236.9,"Q4FY25":4050.8,
         "Q1FY26":3377.4,"Q2FY26":3849.9,"Q3FY26E":3334.0,"Q4FY26E":4191.7}
season = [0.225,0.258,0.229,0.287]
reported = {"Q1FY24":5.3,"Q2FY24":4.5,"Q3FY24":4.3,"Q4FY24":6.6,"Q1FY25":4.5,"Q2FY25":5.0,"Q3FY25":5.7,"Q4FY25":3.1,
            "Q1FY26":6.0,"Q2FY26":4.9}
cons = {"Q3FY26E":1.69,"Q4FY26E":1.59,"Q1FY27E":2.41,"Q2FY27E":2.24}
GC = 0.3

def py(q):
    # prior-year label
    n = int(q[4:6]); suffix = "E" if q.endswith("E") else ""
    base = f"{q[:2]}FY{n-1}"
    return base if base in sales else base + "E"

def schedule(h_inc, f_inc):
    rows = []
    for i, q in enumerate(Q):
        inc = 0.0
        for j in range(max(0, i-4), i+1):
            lag = i - j
            w = 0.5 if lag in (0, 4) else 1.0
            ann = hos_open[j]*reloc_share(Q[j],"H")*h_inc + fh_open[j]*reloc_share(Q[j],"F")*f_inc
            inc += ann * season[i % 4] * w
        base = sales.get(py(q))
        bps = inc / base * 1e4 if base else None
        rows.append((q, inc, base, bps))
    return rows

if __name__ == "__main__":
    out = []
    print("Quarter | format incr $M | PY base $M | format bps (H$20M/F$2.5M) | low (H$15M/F$1.5M) | high (H$25M/F$3.5M) | comp (rep/cons) | implied underlying = comp - format - GC")
    base_r = schedule(20, 2.5); low_r = schedule(15, 1.5); high_r = schedule(25, 3.5)
    for (q, inc, b, bps), (_, _, _, lo), (_, _, _, hi) in zip(base_r, low_r, high_r):
        comp = reported.get(q, cons.get(q))
        und = None if comp is None or bps is None else comp - bps/100 - GC
        print(f"{q} | {inc:6.1f} | {b} | {bps:5.0f} | {lo:5.0f} | {hi:5.0f} | {comp} | {None if und is None else round(und,2)}")
        out.append([q, round(inc,1), b, round(bps), round(lo), round(hi), comp, None if und is None else round(und,2)])
    with open(os.path.join(RAW, "F2_format_comp_schedule.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["quarter","format_incremental_sales_$M","py_base_sales_$M","format_bps_base","format_bps_low","format_bps_high","comp_reported_or_cons","implied_underlying_comp_pct"]); w.writerows(out)
    # FY aggregates
    for fy in ["FY24","FY25","FY26"]:
        idx = [i for i,q in enumerate(Q) if fy in q]
        inc = sum(base_r[i][1] for i in idx); b = sum(base_r[i][2] for i in idx)
        print(f"{fy} format contribution ~{inc/b*100:.2f} pts (base case)")

    # Sales per gross sq ft (DICK'S Business; consistent basis from FY25 incl Warehouse Sale stores)
    sq = {"Q1FY25":45.0,"Q2FY25":45.1,"Q3FY25":45.7,"Q4FY25":45.5,"Q1FY26":45.6,"Q2FY26":46.0}
    rows = []
    for q, prev in [("Q1FY26","Q1FY25"),("Q2FY26","Q2FY25")]:
        g_s = sales[q]/sales[prev]-1; g_sq = sq[q]/sq[prev]-1
        rows.append([q, round(g_s*100,2), round(g_sq*100,2), round(((1+g_s)/(1+g_sq)-1)*100,2)])
    s1 = sales["Q1FY26"]+sales["Q2FY26"]; s0 = sales["Q1FY25"]+sales["Q2FY25"]
    a1 = (sq["Q1FY26"]+sq["Q2FY26"])/2; a0 = (sq["Q1FY25"]+sq["Q2FY25"])/2
    rows.append(["1H FY26", round((s1/s0-1)*100,2), round((a1/a0-1)*100,2), round(((s1/s0)/(a1/a0)-1)*100,2)])
    # FY25: FYE24 43.6M excl 29 Warehouse Sale stores (1.3M sq ft) -> restated 44.9M; FYE25 45.5M
    fy25_sales_g = 14108.9/13442.8-1
    rows.append(["FY25 (end-yr sq ft, WS-restated base 44.9M)", round(fy25_sales_g*100,2), round((45.5/44.9-1)*100,2), round(((1+fy25_sales_g)/(45.5/44.9)-1)*100,2)])
    rows.append(["FY25 (Wells basis 43.6M unrestated)", round(fy25_sales_g*100,2), round((45.5/43.6-1)*100,2), None])
    print("\nPeriod | DICK'S sales y/y % | gross sq ft y/y % | sales per sq ft y/y %")
    for r in rows: print(" | ".join(str(x) for x in r))
    print(f"Warehouse Sale reclass share of FYE24 sq ft: 1.3/43.6 = {1.3/43.6*1e4:.0f} bps")
    with open(os.path.join(RAW, "F2_sqft_productivity.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["period","dks_sales_yoy_pct","gross_sqft_yoy_pct","sales_per_sqft_yoy_pct"]); w.writerows(rows)
