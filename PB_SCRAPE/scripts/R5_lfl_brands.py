"""R5: like-for-like owned-brand new-style counts: styles of season Y (item-id prefix) that had their FIRST REVIEW by
the same calendar date in year Y (as-of date of the catalog pull), by brand; plus all styles created (incl. unreviewed).
Input : latest raw/R5_catalog_brands_*.csv ; Output: raw/R5_lfl_owned_brands.csv ; Rerun: python R5_lfl_brands.py
"""
import glob, os
import pandas as pd

RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\PB_SCRAPE\raw"
f = sorted(glob.glob(os.path.join(RAW, "R5_catalog_brands_*.csv")))[-1]
MMDD = os.path.basename(f)[-12:-8] if False else os.path.basename(f).split("_")[-1][4:8]
MMDD = MMDD[:2] + "-" + MMDD[2:]
G = {"Calia": "CALIA", "CALIA_by_Carrie_Underwood": "CALIA", "Walter_Hagen": "Walter Hagen", "Lady_Hagen": "Walter Hagen",
     "DICK_S_Sporting_Goods": "DSG", "DSG": "DSG", "VRST": "VRST", "Maxfli": "Maxfli", "Top_Flite": "Top Flite",
     "Tommy_Armour_Golf": "Tommy Armour", "Alpine_Design": "Alpine Design", "ETHOS": "ETHOS", "Fitness_Gear": "Fitness Gear",
     "Nishiki": "Nishiki", "Quest": "Quest"}
d = pd.read_csv(f, dtype=str).drop_duplicates("product_id")
d = d[d.brand_id.isin(G)].copy()
d["grp"] = d.brand_id.map(G)
d["fs"] = pd.to_datetime(d.first_sub, errors="coerce", utc=True).dt.tz_localize(None)
rows = []
for s in ["23", "24", "25", "26"]:
    t = d[d.pre == s]
    cut = pd.Timestamp(f"20{s}-{MMDD}")
    for g, u in t.groupby("grp"):
        rows.append(dict(season="20" + s, brand=g, all_styles_now=len(u), reviewed_by_cut=int((u.fs <= cut).sum())))
    rows.append(dict(season="20" + s, brand="TOTAL core owned", all_styles_now=len(t), reviewed_by_cut=int((t.fs <= cut).sum())))
r = pd.DataFrame(rows)
r.to_csv(os.path.join(RAW, "R5_lfl_owned_brands.csv"), index=False)
pd.set_option("display.width", 200)
print("cut", MMDD)
print(r.pivot(index="brand", columns="season", values=["reviewed_by_cut", "all_styles_now"]).fillna(0).astype(int).to_string())
