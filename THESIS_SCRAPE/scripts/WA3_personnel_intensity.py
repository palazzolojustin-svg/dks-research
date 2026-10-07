"""WA3: DICK'S-business personnel intensity and SG&A split, FY22-1H26.

Rerun:  python THESIS_SCRAPE\\scripts\\WA3_personnel_intensity.py
Inputs (hard-coded from filings, see comments) + THESIS_SCRAPE\\raw\\WA3_bls_ahe.json
(BLS CES4200000003 retail AHE all employees, CES4200000008 prod/nonsup; fetched 2026-10-07
from https://api.bls.gov/publicAPI/v1/timeseries/data/). Output: THESIS_SCRAPE\\raw\\WA3_personnel_intensity.csv
"""
import json, csv, os
BASE = r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE"

# $000. Personnel: 10-K FY24 Note 16 (FY22-FY24) and FY25 Note 17 (FY23-FY25) (W01).
pers = {"FY22": 1634510, "FY23": 1838554, "FY24": 1869257, "FY25": 1972850}
sales = {"FY22": 12368198, "FY23": 12984399, "FY24": 13442849, "FY25": 14108943}
weeks = {"FY22": 52, "FY23": 53, "FY24": 52, "FY25": 52}
wk53_sales = 170223  # FY23 53rd week sales (8-K 2024-03-14)
# Non-GAAP SG&A (ex deferred comp, ex business optimization; FY23 restated for grand-opening reclass):
# FY23 3,096,741 / FY24 3,270,635 (8-K 2025-03-11 EX-99.1 recon, W05B); FY25 DICK'S = FY24 + 219,900 (10-K FY25 MD&A, W01)
sga = {"FY23": 3096741, "FY24": 3270635, "FY25": 3270635 + 219900}
# Year-end sq ft (M). FY22-FY24 ex Warehouse Sale (8-K store tables, W05A/B); FY24 restated incl Warehouse 44.8; FY25 45.5 (W04/W01)
sqft = {"FY21": 42.3, "FY22": 42.6, "FY23": 42.7, "FY24": 43.6, "FY24r": 44.8, "FY25": 45.5}
# Fiscal-year month windows (Feb..Jan) for BLS averaging
fy_months = {"FY22": (2022, 2), "FY23": (2023, 2), "FY24": (2024, 2), "FY25": (2025, 2)}

bls = json.load(open(os.path.join(BASE, "raw", "WA3_bls_ahe.json")))
def series_map(sid):
    return {(int(y), int(p[1:])): float(v) for y, p, v in bls[sid] if p.startswith("M") and p != "M13"}
def fy_avg(m, start_year):
    vals = []
    for k in range(12):
        mo = 2 + k; yr = start_year
        if mo > 12: mo -= 12; yr += 1
        if (yr, mo) in m: vals.append(m[(yr, mo)])
    return sum(vals) / len(vals), len(vals)
def win_avg(m, y0, mo0, n):
    vals = []
    for k in range(n):
        mo = mo0 + k; yr = y0
        while mo > 12: mo -= 12; yr += 1
        vals.append(m[(yr, mo)])
    return sum(vals) / n

rows = []
ahe_all = series_map("CES4200000003"); ahe_pn = series_map("CES4200000008")
prev = None
for fy in ["FY22", "FY23", "FY24", "FY25"]:
    p = pers[fy]; s = sales[fy]
    p52 = p * 52 / weeks[fy]; s52 = s - (wk53_sales if fy == "FY23" else 0)
    sq = sqft["FY24r"] if False else sqft[fy]
    a_all, n1 = fy_avg(ahe_all, fy_months[fy][0]); a_pn, n2 = fy_avg(ahe_pn, fy_months[fy][0])
    r = dict(fy=fy, personnel_k=p, sales_k=s, pers_pct=round(100 * p / s, 2),
             pers_pct_52wk=round(100 * p52 / s52, 2), sqft_end_m=sq,
             pers_per_sqft=round(p / 1000 / sq, 2), pers52_per_sqft=round(p52 / 1000 / sq, 2),
             ahe_all=round(a_all, 3), ahe_pn=round(a_pn, 3),
             sga_ng_k=sga.get(fy), sga_pct=round(100 * sga[fy] / s, 2) if fy in sga else None,
             nonpers_sga_pct=round(100 * (sga[fy] - p) / s, 2) if fy in sga else None)
    rows.append(r)

# growth rates (52-wk adjusted where relevant; FY25 per-sqft on restated FY24 44.8 basis)
for i in range(1, len(rows)):
    a, b = rows[i - 1], rows[i]
    b["pers_g"] = round(100 * (b["personnel_k"] / a["personnel_k"] - 1), 1)
    pa = a["personnel_k"] * 52 / weeks[a["fy"]]; pb = b["personnel_k"] * 52 / weeks[b["fy"]]
    b["pers_g_52wk"] = round(100 * (pb / pa - 1), 1)
    sa = a["sales_k"] - (wk53_sales if a["fy"] == "FY23" else 0); sb = b["sales_k"] - (wk53_sales if b["fy"] == "FY23" else 0)
    b["sales_g_52wk"] = round(100 * (sb / sa - 1), 1)
    sq_a = sqft["FY24r"] if (a["fy"] == "FY24" and b["fy"] == "FY25") else a["sqft_end_m"]
    b["pers_per_sqft_g_52wk"] = round(100 * ((pb / b["sqft_end_m"]) / (pa / sq_a) - 1), 1)
    b["ahe_all_g"] = round(100 * (b["ahe_all"] / a["ahe_all"] - 1), 1)
    b["ahe_pn_g"] = round(100 * (b["ahe_pn"] / a["ahe_pn"] - 1), 1)
    b["intensity_g_all"] = round(b["pers_per_sqft_g_52wk"] - b["ahe_all_g"], 1)
    b["intensity_g_pn"] = round(b["pers_per_sqft_g_52wk"] - b["ahe_pn_g"], 1)

# 1H26 vs 1H25 (D07 quarterly personnel; sq ft ~+2% per D07: 45.0->46.0 approx)
h1_25 = 455238 + 486648; h1_26 = 499482 + 530387
ahe1 = win_avg(ahe_all, 2026, 2, 6) / win_avg(ahe_all, 2025, 2, 6) - 1
ahe2 = win_avg(ahe_pn, 2026, 2, 6) / win_avg(ahe_pn, 2025, 2, 6) - 1
pg = h1_26 / h1_25 - 1
rows.append(dict(fy="1H26", personnel_k=h1_26, pers_g=round(100 * pg, 1), pers_per_sqft_g_52wk=round(100 * ((1 + pg) / 1.02 - 1), 1),
                 ahe_all_g=round(100 * ahe1, 1), ahe_pn_g=round(100 * ahe2, 1),
                 intensity_g_all=round(100 * ((1 + pg) / 1.02 - 1) - 100 * ahe1, 1),
                 intensity_g_pn=round(100 * ((1 + pg) / 1.02 - 1) - 100 * ahe2, 1)))

keys = sorted({k for r in rows for k in r}, key=lambda k: list(rows[1].keys()).index(k) if k in rows[1] else 99)
with open(os.path.join(BASE, "raw", "WA3_personnel_intensity.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); [w.writerow(r) for r in rows]
for r in rows:
    print(r)
