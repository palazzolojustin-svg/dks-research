"""F1: HoS/FH relocation-cohort comp calendar and implied ex-format comp vs consensus.

Rerun:  python THESIS_SCRAPE\\scripts\\F1_hos_cohort_comp.py
Output: printed table + THESIS_SCRAPE\\raw\\F1_hos_cohort_comp.csv

Method (INFERENCE, all assumptions labelled):
- Store counts at fiscal quarter-ends from DKS 10-Qs/10-Ks (CORE_NOTES\\C01_SYNTHESIS_A.md, Financial
  Statements section 6b; 10-K FY2025 store table). Openings per quarter = change in count.
- Future openings: FY26 plan ~14 HoS (=> 49 at FYE26, = Bloomberg consensus 49) and ~20 FH (=> 62);
  FY27 18 HoS (under construction, mgmt) and ~19 FH (Bloomberg FH 81 FY27E). Quarterly split assumed.
- A relocated store adds incremental sales y/y for its first 12 months in the comp base (comp counts
  relocations; Gupta 2024-11-26: HoS relocations "will continue to remain in our comp").
  Weight per cohort: opening quarter 0.5, next three quarters 1.0, anniversary quarter 0.5.
- Net uplift per relocated HoS = $35M yr-1 (co slide) - ~$15M displaced box (UBS) = $20M/yr.
  Net uplift per relocated FH = $3M/yr (assumption; co gives only $14M gross yr-1 sales).
- Relocation share: HoS 0.8 (FY25 13 of 16 were conversions), FH 0.87 (13 of 15).
- Comp contribution (pts) = sum(weight * share * uplift) / prior-fiscal-year DKS-segment sales.
- Implied ex-format comp = consensus DKS comp - format contribution (Bloomberg cons 3Q26E 1.69,
  4Q26E 1.59, 1Q27E 2.41, 2Q27E 2.24; actuals for history).
"""
import csv, os

# fiscal quarter labels in order; counts at quarter-end (actual) or plan (assumed)
quarters = [
    # label, HoS count, FH count, actual_comp (None if forecast), consensus comp
    ("Q2FY23", 10, None, 2.0, None),
    ("Q3FY23", 12, None, 1.9, None),
    ("Q4FY23", 12, None, None, None),
    ("Q1FY24", 14, 15, 5.3, None),   # FH ~15 at start FY24 (Gupta: open ~11 in FY24 to reach ~26)
    ("Q2FY24", 14, 17, 4.5, None),   # FH 17 [d] = 22 - 5 opened in Q3FY24
    ("Q3FY24", 17, 22, 4.3, None),
    ("Q4FY24", 19, 26, 6.4, None),
    ("Q1FY25", 21, 31, 4.5, None),
    ("Q2FY25", 22, 35, 5.0, None),
    ("Q3FY25", 35, 41, 5.7, None),
    ("Q4FY25", 35, 42, 3.1, None),
    ("Q1FY26", 36, 44, 6.0, None),
    ("Q2FY26", 41, 52, 4.9, None),
    # forecasts: Bloomberg CONSENSUS quarterly store path (C01A BBG Qtr set A, pulled 2026-10-04):
    # HoS 47/49/53/59, FH 59/63/67/72 for 2027Q3E..2028Q2E (= FQ3FY26..FQ2FY27)
    ("Q3FY26", 47, 59, None, 1.69),
    ("Q4FY26", 49, 63, None, 1.59),
    ("Q1FY27", 53, 67, None, 2.41),
    ("Q2FY27", 59, 72, None, 2.24),
    # BBG Qtr set B: 2028 Q3E / Q4E = FQ3FY27 / FQ4FY27: HoS 66/69, FH 78/81, comp 3.19/3.23
    ("Q3FY27", 66, 78, None, 3.19),
    ("Q4FY27", 69, 81, None, 3.23),
]
import sys
if len(sys.argv) > 1:          # optional: python F1_hos_cohort_comp.py <HoS_uplift_$M> <FH_uplift_$M>
    U_OVERRIDE = (float(sys.argv[1]), float(sys.argv[2]) if len(sys.argv) > 2 else 3.0)
else:
    U_OVERRIDE = None
# prior-fiscal-year DKS segment sales ($M) used as comp denominator (FY24A 13,443; FY25A 14,109; FY26E 14,753)
prior_fy_sales = {"FY23": 12368, "FY24": 12984, "FY25": 13443, "FY26": 14109, "FY27": 14753}

U_HOS, U_FH = 20.0, 3.0   # $M/yr net uplift per relocated store (assumptions)
if U_OVERRIDE:
    U_HOS, U_FH = U_OVERRIDE
S_HOS, S_FH = 0.80, 0.87  # relocation share


def openings(series):
    out = []
    prev = None
    for v in series:
        out.append(None if (v is None or prev is None) else v - prev)
        prev = v if v is not None else prev
    return out


hos_open = openings([q[1] for q in quarters])
fh_open = openings([q[2] for q in quarters])
W = {0: 0.5, 1: 1.0, 2: 1.0, 3: 1.0, 4: 0.5}

rows = []
for i, q in enumerate(quarters):
    e_h = e_f = 0.0
    ok = True
    for lag in range(0, 5):
        j = i - lag
        if j < 0 or hos_open[j] is None:
            ok = False
            continue
        e_h += W[lag] * hos_open[j]
        if fh_open[j] is not None:
            e_f += W[lag] * fh_open[j]
    # comp denominator = prior fiscal year's DKS sales (FY23 quarters -> FY22 sales 12,368)
    denom = prior_fy_sales.get("FY" + str(int(q[0][-2:]) - 1), 12368)
    c_h = e_h * S_HOS * U_HOS / denom * 100
    c_f = e_f * S_FH * U_FH / denom * 100
    comp = q[3] if q[3] is not None else q[4]
    rows.append({
        "quarter": q[0], "hos_count": q[1], "fh_count": q[2],
        "hos_open": hos_open[i], "fh_open": fh_open[i],
        "hos_eff_cohort": round(e_h, 1), "fh_eff_cohort": round(e_f, 1),
        "hos_comp_pts": round(c_h, 2), "fh_comp_pts": round(c_f, 2),
        "format_comp_pts": round(c_h + c_f, 2),
        "comp_used": comp, "comp_type": "actual" if q[3] is not None else ("consensus" if q[4] is not None else ""),
        "ex_format_comp": None if comp is None else round(comp - c_h - c_f, 2),
        "complete_window": ok,
    })

os.makedirs(os.path.join(os.path.dirname(__file__), "..", "raw"), exist_ok=True)
out = os.path.join(os.path.dirname(__file__), "..", "raw", "F1_hos_cohort_comp.csv")
with open(out, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

print("%-7s %4s %4s %5s %5s %6s %6s %6s %6s %6s %6s %s" % ("qtr", "HoS", "FH", "oH", "oF", "effH", "effF", "HoSpt", "FHpt", "comp", "exFmt", "type"))
for r in rows:
    if not r["complete_window"]:
        continue
    print("%-7s %4s %4s %5s %5s %6.1f %6.1f %6.2f %6.2f %6s %6s %s" % (
        r["quarter"], r["hos_count"], r["fh_count"], r["hos_open"], r["fh_open"], r["hos_eff_cohort"],
        r["fh_eff_cohort"], r["hos_comp_pts"], r["fh_comp_pts"], r["comp_used"], r["ex_format_comp"], r["comp_type"]))
print("saved", os.path.abspath(out))
