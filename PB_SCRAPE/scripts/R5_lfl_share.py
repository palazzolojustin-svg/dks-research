"""R5: like-for-like owned share of NEW-SEASON styles reaching customers (first review) by the same calendar cut-off,
season 2023-2026, within the census categories (apparel, golf, fitness, outdoor, team sports, footwear, swim),
excluding fan/licensed gear. Owned and national measured on the same category universe.
Input : latest raw/R5_catalog_cats_*.csv ; Output: raw/R5_lfl_share_cutoffs.csv ; Rerun: python R5_lfl_share.py
Caveat: 2025 review volume stepped up ~3x in Jun/Jul-2025 (X01), and Aug/Sep-2026 reviews are not yet fully published.
Both affect owned and national alike, so read the SHARE, not the counts.
"""
import glob, os
import pandas as pd

RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\PB_SCRAPE\raw"
f = sorted(glob.glob(os.path.join(RAW, "R5_catalog_cats_*.csv")))[-1]
OWN = {"Calia", "CALIA_by_Carrie_Underwood", "VRST", "DSG", "Maxfli", "Walter_Hagen", "Lady_Hagen", "Alpine_Design", "ETHOS",
       "Fitness_Gear", "Top_Flite", "Tommy_Armour_Golf", "Nishiki", "Quest", "PRIMED", "Field___Stream",
       "DICK_S_Sporting_Goods", "Tour_Trek", "Monarch"}
raw = pd.read_csv(f, dtype=str)
fwids = set(raw[raw["query"].str.contains("Footwear|Slides")].product_id)
d = raw.drop_duplicates("product_id").copy()
d["own"] = d.brand_id.isin(OWN)
d["fs"] = pd.to_datetime(d.first_sub, errors="coerce", utc=True).dt.tz_localize(None)
lic = d.name.fillna("").str.contains(r"\b(?:NFL|MLB|NBA|NHL|NCAA|MLS|WNBA)\b|University|State |College|Collegiate| Jersey|Fanatics", regex=True)
d = d[~lic]
rows = []
for scope, u in [("all census cats", d), ("ex-footwear", d[~d.product_id.isin(fwids)])]:
    for cut in ["03-31", "04-30", "05-31", "06-30", "07-31", "08-15", "08-31"]:
        for s in ["23", "24", "25", "26"]:
            t = u[(u.pre == s) & (u.fs <= pd.Timestamp(f"20{s}-{cut}"))]
            rows.append(dict(scope=scope, cut=cut, season="20" + s, styles=len(t), owned=int(t.own.sum()),
                             owned_share=round(t.own.mean(), 4) if len(t) else None))
r = pd.DataFrame(rows)
r.to_csv(os.path.join(RAW, "R5_lfl_share_cutoffs.csv"), index=False)
pd.set_option("display.width", 200)
print(r.pivot_table(index=["scope", "cut"], columns="season", values=["owned", "styles", "owned_share"]).to_string())
