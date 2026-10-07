"""R5: 'DKS-made' brand detector. A style whose UPCs come from DKS's own GS1 company prefixes was set up (sourced)
by DKS itself, i.e. owned brand OR a brand DKS makes under licence/exclusive. Tabulates such styles by brand x season.
Input : latest raw/R5_catalog_cats_*.csv + raw/R5_catalog_brands_*.csv
Output: raw/R5_dks_made_brands_by_season.csv
Rerun : python R5_dks_made_brands.py   (optional: python R5_bv_catalog.py brands Reebok Prince Umbro ... first)
"""
import glob, os
import pandas as pd

RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\PB_SCRAPE\raw"
BLK = ["889751", "889752", "194375", "196358", "198690", "199980"]
fs = sorted(glob.glob(os.path.join(RAW, "R5_catalog_cats_*.csv")))[-1:] + sorted(glob.glob(os.path.join(RAW, "R5_catalog_brands_*.csv")))
d = pd.concat([pd.read_csv(f, dtype=str) for f in fs]).drop_duplicates("product_id").reset_index(drop=True)
d["dks"] = d.upc_prefixes.fillna("").apply(lambda s: any(p in BLK for p in s.split("|")))
d["n_upc"] = pd.to_numeric(d.n_upc, errors="coerce").fillna(0).astype(int)
x = d[d.dks & d.pre.isin([str(i) for i in range(18, 27)])]
t = pd.crosstab(x.brand_name, x.pre)
t["tot"] = t.sum(axis=1)
t = t.sort_values("tot", ascending=False)
t.to_csv(os.path.join(RAW, "R5_dks_made_brands_by_season.csv"))
pd.set_option("display.width", 220); pd.set_option("display.max_rows", 100)
print(t.head(45).to_string())
# share of a brand's styles that are DKS-made, by season (for brands with any DKS-made style)
for b in ["Reebok", "Prince", "Slazenger", "Umbro", "adidas", "Northeast Outfitters", "Second Skin", "Monarch", "Rec League",
          "AD STARR", "Perfect Game", "Marucci", "Cobra", "Lotto", "TaylorMade"]:
    y = d[(d.brand_name == b) & d.pre.isin(["22", "23", "24", "25", "26"])]
    if len(y):
        print(b, y.groupby("pre").dks.agg(["size", "sum"]).T.to_dict())
