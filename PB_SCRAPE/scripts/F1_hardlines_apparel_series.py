"""F1: derive quarterly DICK'S-Business category growth (hardlines) from 10-K/10-Q category tables.

Rerun: python PB_SCRAPE\\scripts\\F1_hardlines_apparel_series.py
Inputs are hard-coded from CORE_NOTES\\C01_SYNTHESIS_A.md section 7 (Financial Statements synthesis)
and WORKING_NOTES\\W04 (10-Q Note 8 revenue disaggregation). Update the dict when a new 10-Q prints.
Logic: Foot Locker reports footwear + "apparel & accessories" only (FY24 FL: footwear 84%/apparel &
accessories 16%), and DKS defines hardlines as sporting goods equipment, fitness, golf, fishing, so
consolidated hardlines after the FL close (2025-09-08) is treated as ~100% DICK'S Business (INFERENCE).
Apparel cannot be split after the close (FL apparel is inside it), so apparel growth is only computed pre-FL.
Output: PB_SCRAPE\\raw\\F1_hardlines_series.csv
"""
import csv, os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "PB_SCRAPE", "raw", "F1_hardlines_series.csv")

# $M; DICK'S segment sales from segment note (post-FL) or total (pre-FL)
hard = {  # quarter: (hardlines this yr, hardlines prior yr, DKS seg sales this yr, DKS seg sales prior yr)
    "1H FY25 (26w to 2025-08-02)": (2664.4, 3744.8 - 1057.5, 6821.3, 6492.0),
    "Q3 FY25 (to 2025-11-01)": (1104.4, 1057.5, 3236.9, 3057.2),
    "Q4 FY25 (derived FY-39w)": (5048.3 - 3768.9, 4899.3 - 3744.8, 14108.9 - 10058.2, 13442.8 - 9549.2),
    "Q1 FY26 (to 2026-05-02)": (1326.6, 1192.9, 3377.4, 3174.7),
    "Q2 FY26 (to 2026-08-01)": (1552.3, 1471.5, 3849.9, 3646.6),
    "FY24 (annual)": (4899.3, 4915.5, 13442.8, 12984.4),
    "FY25 (annual)": (5048.3, 4899.3, 14108.9, 13442.8),
}
with open(OUT, "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["period", "hardlines_$M", "hardlines_PY_$M", "hardlines_yoy_%", "DKS_seg_sales_yoy_%", "hardlines_share_of_DKS_seg_%", "PY_share_%"])
    for k, (h, hp, s, sp) in hard.items():
        w.writerow([k, round(h, 1), round(hp, 1), round((h / hp - 1) * 100, 1), round((s / sp - 1) * 100, 1), round(h / s * 100, 1), round(hp / sp * 100, 1)])
        print(k, round((h / hp - 1) * 100, 1), round((s / sp - 1) * 100, 1), round(h / s * 100, 1), round(hp / sp * 100, 1))
print("->", OUT)
