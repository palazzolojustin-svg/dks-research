"""F5: consensus-implied 'underlying' DSG comp using the bears' (Wells Fargo) own decomposition,
plus UBS HoS-only contribution, and $/share translation of a comp gap.

Inputs (all from the folder; see THESIS_SCRAPE/wave1/F5.md):
 - BBG consensus DKS (core) comp by quarter (KNOWN_BRIEF / digest 7b)
 - WF Exhibit 17 (2026-08-10 upgrade note): relocation impact 2.2% FY26E / 2.7% FY27E; GameChanger 0.3% / 0.3%
   SOURCE/03_DKS_STREET_RESEARCH/2026-08-17_WellsFargo_DKS_DKS_Upgrade_to_OW_LT_Upside_Outweighs_NT_Noise_PT_to.md lines 1521-1550
 - UBS 2026-05-18: HoS ~170bps avg comp contribution in 2026, ~150bps in 1Q26
 - FY27E: DSG segment revenue $15,203M, segment OI $1,647M, 89.09M shares, 27.46% tax
Rerun: python F5_implied_underlying_comp.py  -> prints table and writes THESIS_SCRAPE/raw/F5_implied_underlying_comp.csv
"""
import csv, os

cons = {"3Q26E": 1.69, "4Q26E": 1.59, "1Q27E": 2.41, "2Q27E": 2.24}
wf_relo = {"3Q26E": 2.2, "4Q26E": 2.2, "1Q27E": 2.7, "2Q27E": 2.7}   # WF annual relo impact applied to quarters
wf_gc = 0.3
ubs_hos = 1.7  # UBS 2026 avg HoS-only contribution (bps/100)
actual = {"1Q26A": (6.0, 2.2), "2Q26A": (4.9, 2.2), "FY25A": (4.5, 2.3)}

rows = []
for q, c in cons.items():
    rows.append({"period": q, "reported_comp": c, "wf_relo": wf_relo[q], "wf_gc": wf_gc,
                 "implied_underlying_wf": round(c - wf_relo[q] - wf_gc, 2),
                 "implied_ex_hos_ubs": round(c - ubs_hos, 2), "type": "consensus"})
for q, (c, r) in actual.items():
    gc = 0.4 if q == "FY25A" else 0.3
    rows.append({"period": q, "reported_comp": c, "wf_relo": r, "wf_gc": gc,
                 "implied_underlying_wf": round(c - r - gc, 2),
                 "implied_ex_hos_ubs": round(c - ubs_hos, 2), "type": "actual"})

# $/share translation of a FY27 comp gap
rev, oi, sh, tax = 15203.0, 1647.0, 89.09, 0.2746
def eps(delta_comp_pct, flow):
    d_sales = rev * delta_comp_pct / 100.0
    d_oi = d_sales * flow
    return d_sales, d_oi, d_oi * (1 - tax) / sh

# Scenario: underlying = WF's own +1.1% + WF relo 2.7 + GC 0.3 = 4.1% vs consensus ~2.33% (avg 1Q27E/2Q27E)
gap = 4.1 - (2.41 + 2.24) / 2
for flow in (oi / rev, 0.20, 0.30):
    s, o, e = eps(gap, flow)
    rows.append({"period": f"FY27 gap {gap:.2f}pp @ flow {flow:.3f}", "reported_comp": "", "wf_relo": "",
                 "wf_gc": "", "implied_underlying_wf": f"dSales ${s:.0f}M dOI ${o:.0f}M",
                 "implied_ex_hos_ubs": f"EPS +${e:.2f}", "type": "translation"})

out = os.path.join(os.path.dirname(__file__), "..", "raw", "F5_implied_underlying_comp.csv")
with open(out, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)
for r in rows:
    print(r)
