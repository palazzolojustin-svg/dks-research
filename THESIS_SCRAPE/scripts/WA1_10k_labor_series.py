"""WA1 (wave 2): DICK'S-segment labor/headcount/landlord series from DKS 10-Ks FY2022-FY2025.

Inputs are hard-coded from the 10-Ks (SOURCE\\01_DKS_SEC_FILINGS\\10-K\\*.md; notes in WORKING_NOTES\\W01/W02):
- Personnel/occupancy/other segment expense: FY24 10-K segment note (FY22-FY24) and FY25 10-K Note 17 (FY23-FY25, DICK'S segment).
- Headcount: 10-K Item 1 Human Capital (FYE). FY25 DICK'S = 105,200 total - 45,400 Foot Locker Business.
- Sq ft / stores: 10-K store-activity tables (FY24/FY25 incl. Warehouse Sale locations on the restated basis).
- 401(k) employer match, accrued payroll, landlord receivables, construction allowances, capex: 10-K notes / cash-flow statements.
Rerun: python WA1_10k_labor_series.py  -> writes ..\\raw\\WA1_10k_labor_series.csv and prints the tables.
"""
import csv, os

FY = ["FY22", "FY23", "FY24", "FY25"]
sales = {"FY22": 12368.198, "FY23": 12984.399, "FY24": 13442.849, "FY25": 14108.943}  # DICK'S segment $M
sales52 = dict(sales, FY23=12814.176)  # FY23 ex 53rd week ($170.223M)
personnel = {"FY22": 1634.510, "FY23": 1838.554, "FY24": 1869.257, "FY25": 1972.850}
occupancy = {"FY22": 1059.951, "FY23": 1100.720, "FY24": 1139.387, "FY25": 1197.019}
heads_ft = {"FY22": 18800, "FY23": 18900, "FY24": 18600, "FY25": None}
heads_pt = {"FY22": 34000, "FY23": 36600, "FY24": 37500, "FY25": None}
heads = {"FY22": 52800, "FY23": 55500, "FY24": 56100, "FY25": 105200 - 45400}
sqft = {"FY22": 42.6, "FY23": 42.7, "FY24": 44.8, "FY25": 45.5}  # M gross sq ft; FY24/25 incl Warehouse Sale (restated)
k401 = {"FY21": 24.1, "FY22": 31.6, "FY23": 34.8, "FY24": 36.7, "FY25": 41.2}  # DICK'S plan employer match $M
accr_payroll = {"FY21": 297.409, "FY22": 218.802, "FY23": 212.950, "FY24": 256.881, "FY25": 397.698}  # FY25 incl FL
landlord_ar = {"FY21": 45.0, "FY22": 34.3, "FY23": 72.7, "FY24": 160.2, "FY25": 274.0}  # FY25 consolidated
constr_allow = {"FY22": 36.1, "FY23": 67.061, "FY24": 76.287, "FY25": 161.659}
capex_dks = {"FY22": 364.075, "FY23": 587.426, "FY24": 802.565, "FY25": 1043.463}

rows = []
prev = None
for y in FY:
    s52 = sales52[y]
    pers52 = personnel[y] * (52 / 53 if y == "FY23" else 1)
    r = {
        "FY": y,
        "sales_$M": sales[y],
        "personnel_$M": personnel[y],
        "personnel_pct": round(100 * personnel[y] / sales[y], 2),
        "personnel_pct_52wk": round(100 * pers52 / s52, 2),
        "occupancy_pct": round(100 * occupancy[y] / sales[y], 2),
        "heads_FYE": heads[y],
        "ft_share_pct": round(100 * heads_ft[y] / heads[y], 1) if heads_ft[y] else "",
        "heads_per_1k_sqft": round(heads[y] / (sqft[y] * 1000), 3),
        "sales_per_FYE_head_$K": round(1000 * s52 / heads[y], 1),
        "k401_match_$M": k401[y],
        "landlord_AR_$M": landlord_ar[y],
        "landlord_funding_accrued_$M": round(constr_allow[y] + landlord_ar[y] - landlord_ar[{"FY22": "FY21", "FY23": "FY22", "FY24": "FY23", "FY25": "FY24"}[y]], 1),
    }
    r["landlord_funding_pct_DKS_capex"] = round(100 * r["landlord_funding_accrued_$M"] / capex_dks[y], 1)
    if prev:
        avg_heads = (heads[y] + heads[prev]) / 2
        prev_pers52 = personnel[prev] * (52 / 53 if prev == "FY23" else 1)
        r["personnel_$_per_avg_head_$K"] = round(1000 * pers52 / avg_heads, 2)
        r["heads_yoy_pct"] = round(100 * (heads[y] / heads[prev] - 1), 1)
        r["personnel_52wk_yoy_pct"] = round(100 * (pers52 / prev_pers52 - 1), 1)
        r["sales_52wk_yoy_pct"] = round(100 * (s52 / sales52[prev] - 1), 1)
        r["k401_yoy_pct"] = round(100 * (k401[y] / k401[prev] - 1), 1)
    rows.append(r)
    prev = y

keys = []
for r in rows:
    for k in r:
        if k not in keys:
            keys.append(k)
out = os.path.join(os.path.dirname(__file__), "..", "raw", "WA1_10k_labor_series.csv")
with open(out, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=keys)
    w.writeheader()
    for r in rows:
        w.writerow(r)
for r in rows:
    print(r)

# Business Optimization analog: FY23 severance $26.7M (CSC-heavy) -> FY24 personnel leverage
lev_rep = 100 * (personnel["FY24"] / sales["FY24"] - personnel["FY23"] / sales["FY23"])
lev_52 = 100 * (personnel["FY24"] / sales["FY24"] - personnel["FY23"] * 52 / 53 / sales52["FY23"])
print("FY24 personnel leverage bp reported %.1f, 52wk-adjusted %.1f" % (lev_rep * 100, lev_52 * 100))
print("$ value at FY24 sales: reported %.1fM, 52wk %.1fM vs severance 26.7M" % (-lev_rep / 100 * sales["FY24"], -lev_52 / 100 * sales["FY24"]))
