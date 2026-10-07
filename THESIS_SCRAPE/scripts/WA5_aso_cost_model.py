"""WA5: Academy (ASO) store-cost productivity series vs DICK'S.
Inputs hard-coded from ASO 10-K/10-Q text (WORKING_NOTES/P_ASO_10K.md, P_ASO_10Q.md and EDGAR pulls in
raw/WA5_aso_sga_bridges.txt, raw/WA5_aso_headcount.csv) and DKS 10-K headcount (WA1, W01/W02).
Rerun: python THESIS_SCRAPE/scripts/WA5_aso_cost_model.py -> raw/WA5_aso_cost_series.csv
"""
import csv, os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# quarterly ASO SG&A ($M), end stores, strategic investment $M (company-stated, y/y increment), headcount (approx)
q = [
 # label, SGA, SGA_py, stores_end, stores_begin, stores_end_py, stores_begin_py, strategic, other_named, headcount, headcount_py
 ("Q1FY24", 353.4, 340.9, 284, 282, 269, 268, 16.3, 0, 22000, 22000),
 ("Q2FY24", 368.6, 352.5, 285, 284, 270, 269, 17.1, 0, 21000, 22000),
 ("Q3FY24", 365.2, 345.9, 293, 285, 275, 270, 17.5, 0, 23000, 22000),
 ("Q1FY25", 389.6, 353.4, 303, 298, 284, 282, 33.4, 0, 22000, 22000),
 ("Q2FY25", 404.4, 368.6, 306, 303, 285, 284, 26.9, 0, 23000, 21000),   # strategic derived: 85.0-33.4-24.7
 ("Q3FY25", 393.0, 365.2, 317, 306, 293, 285, 24.7, 0, 24000, 23000),
 ("Q4FY25", 406.5, 385.5, 322, 317, 298, 293, 24.0, 0, 23000, 22000),   # derived FY-9M; strategic 109.0-85.0
 ("Q1FY26", 404.7, 389.6, 324, 322, 303, 298, 19.0, -7.5, 22000, 22000), # -7.5 Jordan launch lap
 ("Q2FY26", 419.5, 404.4, 327, 324, 306, 303, 19.1, 0, 22000, 23000),
]
rows = []
for (lab, s, spy, se, sb, sepy, sbpy, strat, oth, hc, hcpy) in q:
    avg, avgpy = (se + sb) / 2, (sepy + sbpy) / 2
    base = (s - spy) - strat - oth
    rows.append(dict(q=lab, sga=s, sga_yoy=round(100 * (s / spy - 1), 1), stores_yoy=round(100 * (se / sepy - 1), 1),
                     sga_per_store_yoy=round(100 * ((s / avg) / (spy / avgpy) - 1), 1),
                     base_cost_change=round(base, 1), base_pct_of_py=round(100 * base / spy, 1),
                     headcount=hc, headcount_yoy=round(100 * (hc / hcpy - 1), 1),
                     staff_per_store=round(hc / se, 1), staff_per_store_py=round(hcpy / sepy, 1)))
# LTM sales per team member (ASO)
ltm = {"FY21": (6773.0, 22000), "FY22": (6395.1, 22000), "FY23": (6159.3, 22000), "FY24": (5933.5, 22000),
       "FY25": (6053.4, 23000), "LTM Aug-25": (5933.5 + 2951.2 - 2913.2, 23000), "LTM Aug-26": (6053.4 + 3089.3 - 2951.2, 22000)}
with open(os.path.join(BASE, "raw", "WA5_aso_cost_series.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
for r in rows: print(r)
for k, (s, h) in ltm.items(): print(k, "sales/team member $K", round(s / h * 1000, 1))
# DICK'S comparison (WA1/W01-W02): DICK'S Business year-end employees and DICK'S segment sales ($M)
dks = {"FY22": (12368.2, 52800), "FY23": (12984.4, 55500), "FY24": (13442.8, 56100), "FY25": (14108.9, 59800)}
for k, (s, h) in dks.items(): print("DKS", k, "sales/employee $K", round(s / h * 1000, 1))
print("ASO staff per 1,000 sq ft FY25:", round(23000 / 21900, 2), " DKS:", round(59800 / 45500, 2))
