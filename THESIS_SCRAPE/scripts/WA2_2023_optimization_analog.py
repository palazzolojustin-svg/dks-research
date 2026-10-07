"""WA2 (wave 2): the 2023 "Business Optimization" as an analog for the 2026 "Built to Win" store-labor redesign.

Inputs are hard-coded from DKS 10-Q/10-K figures recorded in WORKING_NOTES (W01, W02, W03, W04, W06)
and verified against SOURCE\\01_DKS_SEC_FILINGS. All $ in millions.
Rerun:  python THESIS_SCRAPE\\scripts\\WA2_2023_optimization_analog.py
Output: THESIS_SCRAPE\\raw\\WA2_2023_analog.csv (+ printed tables)
"""
import csv, os

OUT = os.path.join(os.path.dirname(__file__), "..", "raw", "WA2_2023_analog.csv")
rows = []

def add(section, item, value, note=""):
    rows.append({"section": section, "item": item, "value": value, "note": note})
    print(f"{section:<28} {item:<60} {value:>10} {note}")

# ---------- 1. Annual DICK'S-business personnel (CODM table; excludes business-optimization and redesign charges,
#               which sit in 'corporate & other': FY23 corp&other 98.773 = 84.813 optimization + 13.960 deferred comp)
sales = {"FY22": 12368.198, "FY23": 12984.399, "FY24": 13442.849, "FY25": 14108.943}
pers = {"FY22": 1634.510, "FY23": 1838.554, "FY24": 1869.257, "FY25": 1972.850}
add("check", "FY23 corp&other = optimization 84.813 + def comp 13.960", round(84.813 + 13.960, 3), "vs 10-K 98.773")
prev = None
for fy in sales:
    pct = pers[fy] / sales[fy] * 100
    add("personnel annual", f"{fy} personnel % of DICK'S sales", round(pct, 2))
    if prev:
        add("personnel annual", f"{fy} personnel $ y/y %", round((pers[fy] / pers[prev] - 1) * 100, 1),
            f"sales y/y {round((sales[fy]/sales[prev]-1)*100,1)}%")
        add("personnel annual", f"{fy} personnel $ change", round(pers[fy] - pers[prev], 1))
    prev = fy

# 53rd week adjustment (FY23 had 53 weeks; 53rd week sales $170.2M). Assume personnel accrues pro rata to weeks.
wk53_sales = 170.2
fy23_sales52 = sales["FY23"] - wk53_sales
fy23_pers52 = pers["FY23"] * 52 / 53
add("53wk adj", "FY23 52-wk sales", round(fy23_sales52, 1))
add("53wk adj", "FY23 52-wk personnel (pro rata)", round(fy23_pers52, 1), "ASSUMPTION")
add("53wk adj", "FY23 52-wk personnel %", round(fy23_pers52 / fy23_sales52 * 100, 2))
add("53wk adj", "FY24 personnel y/y % (52 vs 52)", round((pers["FY24"] / fy23_pers52 - 1) * 100, 1),
    f"sales {round((sales['FY24']/fy23_sales52-1)*100,1)}%")
add("53wk adj", "FY24 personnel bp change (52 vs 52)",
    round((pers["FY24"] / sales["FY24"] - fy23_pers52 / fy23_sales52) * 1e4, 0))

# 'Savings' in FY24 vs personnel growing in line with sales
for label, base_p, g in [("reported", pers["FY23"], sales["FY24"] / sales["FY23"]),
                         ("52wk-adj", fy23_pers52, sales["FY24"] / fy23_sales52)]:
    counterfactual = base_p * g
    saving = counterfactual - pers["FY24"]
    add("analog saving", f"FY24 personnel below sales-growth path ({label})", round(saving, 1),
        f"= {round(saving/26.7,2)}x the $26.7M 2023 severance")

# ---------- 2. SG&A drivers attributed to 'hourly wage rates, talent, technology' (MD&A)
add("wage investment", "FY22 SG&A increase: wage rates/talent/tech", 127.1, "10-K FY22; offset by lower incentive comp")
add("wage investment", "Q1 FY23 SG&A increase: hourly wage rates/talent/tech", 78.6 - 10.0, "+$78.6M incl $10.0M def comp")
add("wage investment", "Q2 FY23 wage rates/talent/tech", 51.5, "10-Q")
add("wage investment", "Q3 FY23 wage/talent/tech + marketing", 33.7, "10-Q")
add("wage investment", "39w FY23 wage/talent/tech", 139.9, "10-Q Q3 FY23")
add("wage investment", "FY23 wage/talent/tech", 191.7, "10-K FY23")
add("wage investment", "Q4 FY23 implied", round(191.7 - 139.9, 1), "[d]")

# ---------- 3. Q4 FY23 SG&A vs guidance ('moderate ~150bp from Q3')
sga_fy23, sga_39w23 = 3204.1, 2245.530
q4_sales23 = sales["FY23"] - 9108.228
q4_sga23 = sga_fy23 - sga_39w23
q3_sga_pct = 776.037 / 3042.405 * 100
q4_sga_pct = q4_sga23 / q4_sales23 * 100
q4_opt = 72.8 - 46.2   # optimization charges in SG&A booked in Q4
add("Q4 FY23 check", "Q3 FY23 SG&A % (reported)", round(q3_sga_pct, 2))
add("Q4 FY23 check", "Q4 FY23 SG&A % (reported, implied)", round(q4_sga_pct, 2), f"moderation {round(q3_sga_pct-q4_sga_pct,0)*100/100}pp")
add("Q4 FY23 check", "Q4 FY23 SG&A % ex $26.6M Q4 optimization", round((q4_sga23 - q4_opt) / q4_sales23 * 100, 2),
    f"guide ~{round(q3_sga_pct-1.5,2)}%")

# ---------- 4. Total SG&A after the action (FY24 vs FY23 recast for grand-opening reclass)
sga23r, sga24 = 3183.5, 3294.3
add("SG&A FY24", "FY23 SG&A % (recast, reported)", round(sga23r / sales["FY23"] * 100, 2))
add("SG&A FY24", "FY23 SG&A % ex $72.8M optimization", round((sga23r - 72.8) / sales["FY23"] * 100, 2))
add("SG&A FY24", "FY24 SG&A %", round(sga24 / sales["FY24"] * 100, 2))
add("SG&A FY24", "FY24 SG&A % ex +$9.7M def-comp increase", round((sga24 - 9.7) / sales["FY24"] * 100, 2))
add("SG&A FY24", "FY24 vs FY23 ex-charges (bp)", round((sga24 / sales["FY24"] - (sga23r - 72.8) / sales["FY23"]) * 1e4, 0))
seg_other = {"FY23": 1999.775, "FY24": 2122.954, "FY25": 2269.702}
for fy in seg_other:
    add("segment other exp", f"{fy} other segment expenses % of sales", round(seg_other[fy] / sales[fy] * 100, 2))
seg_profit = {"FY23": 1381.138, "FY24": 1497.569, "FY25": 1568.443}
for fy in seg_profit:
    add("segment margin", f"{fy} DICK'S segment margin %", round(seg_profit[fy] / sales[fy] * 100, 2))

# ---------- 5. Quarterly SG&A $ growth vs sales growth (consolidated, pre-FL), FY24 recast basis
q = [("Q1 FY24", 743.399, 693.845, 3018.383, 2842.181, 45),
     ("Q2 FY24", 796.673, 764.788, 3473.635, 3223.643, 95),
     ("Q3 FY24", 790.621, 768.188, 3057.181, 3042.405, -105)]
for name, s1, s0, n1, n0, shift in q:
    add("quarterly SG&A", f"{name} SG&A y/y %", round((s1 / s0 - 1) * 100, 1),
        f"sales {round((n1/n0-1)*100,1)}%; ex calendar shift {round(((n1-shift)/n0-1)*100,1)}%")

# ---------- 6. Variance translation for Built to Win (INFERENCE)
dsg_rev_fy27 = 15203.0
per_m = 0.00814
for mult in (0.86, 1.26):
    sav = 21.0 * mult
    add("variance (INFERENCE)", f"Built to Win yr-1 saving at {mult}x the ~$21M charge ($M)", round(sav, 1),
        f"{round(sav/dsg_rev_fy27*1e4,0)}bp DSG margin; ${round(sav*per_m,2)}/sh")

with open(OUT, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["section", "item", "value", "note"])
    w.writeheader(); w.writerows(rows)
print("wrote", os.path.abspath(OUT))
