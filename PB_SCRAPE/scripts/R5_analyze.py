"""R5: analyse the all-brand category catalog census (Bazaarvoice products) for owned-brand style share by season.

Input : raw/R5_catalog_cats_<date>.csv   (python R5_bv_catalog.py cats)
Output: raw/R5_style_share_by_group_season.csv  (group, season, owned/national styles + SKUs, shares)
        raw/R5_lfl_asof.csv                     (like-for-like: styles of season Y first reviewed by <MM-DD> of year Y)
        raw/R5_brand_styles_by_season.csv       (top brands' style counts by group x season)
        printed summary
Season = 2-digit prefix of the DKS item id (25xxxx = 2025 season; ~= DKS fiscal year of launch, see R5.md).
Rerun : python R5_analyze.py [cats csv]   (re-pull monthly; compare the 26-vs-25 LFL at the same MM-DD)
"""
import sys, glob, os
import pandas as pd

RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\PB_SCRAPE\raw"
f = sys.argv[1] if len(sys.argv) > 1 else sorted(glob.glob(os.path.join(RAW, "R5_catalog_cats_*.csv")))[-1]
ASOF = os.path.basename(f).split("_")[-1][:8]  # yyyymmdd
MMDD = ASOF[4:6] + "-" + ASOF[6:8]
OWNED = {"Calia", "CALIA_by_Carrie_Underwood", "VRST", "DSG", "Maxfli", "Walter_Hagen", "Lady_Hagen", "Alpine_Design",
         "ETHOS", "Fitness_Gear", "Top_Flite", "Tommy_Armour_Golf", "Nishiki", "Quest", "PRIMED", "Field___Stream",
         "DICK_S_Sporting_Goods", "Tour_Trek", "Monarch"}
GROUP = {"WomensApparel-129841": "Women's apparel", "MensApparel-129824": "Men's apparel",
         "BoysApparel-129859": "Kids apparel", "girls-apparel-footwear": "Kids apparel",
         "Golf-129239": "Golf", "ExerciseFitness-128988": "Fitness", "CampingHiking-128904": "Outdoor/camp/bike",
         "BikesCycling-128852": "Outdoor/camp/bike", "Outdoor-236211": "Outdoor/camp/bike",
         "ShopBySport-128771": "Team sports", "MensFootwear-129886": "Footwear", "WomensFootwear-129911": "Footwear",
         "YouthFootwear-129933": "Footwear", "Slides-Flip-Flops": "Footwear", "Footwear-129885": "Footwear",
         "WomensSwimsuits-129848": "Women's apparel"}
LICENSED_HINT = r"\b(?:NFL|MLB|NBA|NHL|NCAA|MLS|WNBA)\b|University|State |College|Collegiate| Jersey|Fanatics|'47|New Era|Nike College|Bulldogs|Tigers|Wildcats"

d = pd.read_csv(f, dtype=str)
d["group"] = d["query"].str.replace("CategoryAncestorId:eq:", "", regex=False).map(GROUP)
d = d.drop_duplicates(["group", "product_id"])
d["owned"] = d.brand_id.isin(OWNED)
d["n_upc"] = pd.to_numeric(d.n_upc, errors="coerce").fillna(0).astype(int)
d["fs"] = pd.to_datetime(d.first_sub, errors="coerce", utc=True).dt.tz_localize(None)
d["fan"] = d.name.fillna("").str.contains(LICENSED_HINT, regex=True)
S = ["22", "23", "24", "25", "26"]
x = d[d.pre.isin(S) & ~d.fan]

rows = []
for (g, s), t in x.groupby(["group", "pre"]):
    o = t[t.owned]
    rows.append(dict(group=g, season="20" + s, styles=len(t), owned_styles=len(o), owned_style_share=len(o) / len(t),
                     skus=t.n_upc.sum(), owned_skus=o.n_upc.sum(), owned_sku_share=o.n_upc.sum() / max(1, t.n_upc.sum()),
                     active_styles=(t.active == "True").sum(), owned_active=(o.active == "True").sum()))
tot = x.groupby("pre")
for s, t in tot:
    tt = t.drop_duplicates("product_id"); o = tt[tt.owned]
    rows.append(dict(group="ALL (dedup)", season="20" + s, styles=len(tt), owned_styles=len(o), owned_style_share=len(o) / len(tt),
                     skus=tt.n_upc.sum(), owned_skus=o.n_upc.sum(), owned_sku_share=o.n_upc.sum() / max(1, tt.n_upc.sum()),
                     active_styles=(tt.active == "True").sum(), owned_active=(o.active == "True").sum()))
share = pd.DataFrame(rows)
share.to_csv(os.path.join(RAW, "R5_style_share_by_group_season.csv"), index=False)

# like-for-like as-of: styles of season Y first reviewed by MM-DD of calendar year Y (and by 06-30)
lfl = []
for cut in [MMDD, "06-30"]:
    for (g, s), t in x.groupby(["group", "pre"]):
        if s not in ("24", "25", "26"):
            continue
        lim = pd.Timestamp(f"20{s}-{cut}")
        r = t[t.fs.notna() & (t.fs <= lim)]
        lfl.append(dict(cut=cut, group=g, season="20" + s, reviewed_styles=len(r), owned=int(r.owned.sum()),
                        owned_share=r.owned.mean() if len(r) else None))
lfl = pd.DataFrame(lfl)
lfl.to_csv(os.path.join(RAW, "R5_lfl_asof.csv"), index=False)

# brand detail
b = x.groupby(["group", "brand_name", "pre"]).size().unstack("pre").fillna(0).astype(int)
b["tot"] = b.sum(axis=1)
b = b.sort_values("tot", ascending=False)
b.to_csv(os.path.join(RAW, "R5_brand_styles_by_season.csv"))

# launch-timing check: of season-Y styles that are reviewed today, share first reviewed by MM-DD of year Y
cf = []
for (g, s, o), t in x[x.fs.notna()].groupby(["group", "pre", "owned"]):
    if s not in ("23", "24", "25"):
        continue
    cf.append(dict(group=g, season="20" + s, owned=o, reviewed=len(t),
                   by_cut=(t.fs <= pd.Timestamp(f"20{s}-{MMDD}")).mean()))
cf = pd.DataFrame(cf)
cf.to_csv(os.path.join(RAW, "R5_launch_timing_cf.csv"), index=False)

pd.set_option("display.width", 250); pd.set_option("display.max_rows", 400)
print("== completion factor (share of eventually-reviewed season-Y styles first reviewed by", MMDD, "of Y)")
print(cf.pivot_table(index="group", columns=["season", "owned"], values="by_cut").round(2).to_string())
print("as-of", ASOF)
print(share.pivot(index="group", columns="season", values="owned_style_share").round(3).to_string())
print(share.pivot(index="group", columns="season", values="owned_sku_share").round(3).to_string())
print(share.pivot(index="group", columns="season", values="styles").to_string())
print(share.pivot(index="group", columns="season", values="owned_styles").to_string())
print(lfl.pivot_table(index=["cut", "group"], columns="season", values=["reviewed_styles", "owned_share"]).round(3).to_string())
for g in b.index.get_level_values(0).unique():
    print("==", g); print(b.loc[g].head(15).to_string())
