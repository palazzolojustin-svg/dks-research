"""R5: (1) check which brands use DKS's own GS1 UPC blocks; (2) owned share of new styles ex-footwear, ex-fan-gear;
(3) UPC 'clock': DKS GS1 block consumption over time.
Rerun: python R5_upc_and_exfw.py  (after R5_bv_catalog.py brands + cats)
"""
import glob, os
import pandas as pd

RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\PB_SCRAPE\raw"
cats = sorted(glob.glob(os.path.join(RAW, "R5_catalog_cats_*.csv")))[-1]
brands = sorted(glob.glob(os.path.join(RAW, "R5_catalog_brands_*.csv")))[-1]
OWN = {"Calia", "CALIA_by_Carrie_Underwood", "VRST", "DSG", "Maxfli", "Walter_Hagen", "Lady_Hagen", "Alpine_Design", "ETHOS",
       "Fitness_Gear", "Top_Flite", "Tommy_Armour_Golf", "Nishiki", "Quest", "PRIMED", "Field___Stream",
       "DICK_S_Sporting_Goods", "Tour_Trek", "Monarch"}
BLK = ["889751", "889752", "194375", "196358", "198690", "199980"]
raw = pd.read_csv(cats, dtype=str)
d = raw.drop_duplicates("product_id").copy()
d["own"] = d.brand_id.isin(OWN)
d["dks"] = d.upc_prefixes.fillna("").apply(lambda s: any(p in BLK for p in s.split("|")))
print("== products using DKS GS1 blocks (rows=owned flag, cols=uses DKS block)")
print(pd.crosstab(d.own, d.dks))
print(d[d.dks & ~d.own].brand_name.value_counts().head(25).to_string())

fwids = set(raw[raw["query"].str.contains("Footwear|Slides")].product_id)
lic = d.name.fillna("").str.contains(r"\b(?:NFL|MLB|NBA|NHL|NCAA|MLS|WNBA)\b|University|State |College|Collegiate| Jersey|Fanatics", regex=True)
y = d[~d.product_id.isin(fwids) & ~lic & d.pre.isin(["21", "22", "23", "24", "25", "26"])]
t = y.groupby("pre").agg(new_styles=("product_id", "size"), owned=("own", "sum"))
t["owned_share"] = (t.owned / t.new_styles).round(4)
print("== owned share of NEW styles, ex-footwear, ex-fan-gear (all census categories, dedup)")
print(t.to_string())
t.to_csv(os.path.join(RAW, "R5_owned_share_new_styles_exfw.csv"))

# UPC clock on owned styles: global sequence S = block index * 100000 + 5-digit item number of the style's lowest UPC
b = pd.read_csv(brands, dtype=str).drop_duplicates("product_id")
b = b[b.upc_min.fillna("").str[:6].isin(BLK)].copy()
b["S"] = b.upc_min.str[:6].map({k: i for i, k in enumerate(BLK)}) * 100000 + b.upc_min.str[6:11].astype(int)
b["fs"] = pd.to_datetime(b.first_sub, errors="coerce", utc=True).dt.tz_localize(None)
z = b.dropna(subset=["fs"])
z = z[z.fs >= "2022-01-01"]
z["q"] = z.fs.dt.to_period("Q")
q = z.groupby("q").S.agg(["count", "median", lambda s: s.quantile(0.9)]).rename(columns={"<lambda_0>": "p90"})
q["median_step"] = q["median"].diff()
print("== UPC clock: sequence of owned styles by quarter of first review")
print(q.astype(int, errors="ignore").to_string())
q.to_csv(os.path.join(RAW, "R5_upc_clock_quarterly.csv"))
