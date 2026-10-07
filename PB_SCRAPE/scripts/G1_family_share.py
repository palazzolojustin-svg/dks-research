"""G1: brand-FAMILY review shares (relabel-neutral) and the effect of excluded exclusive tail brands on owned share.
PIE (post-purchase email) reviews, Apr-Aug 2024/25/26, share of all-brand PIE reviews in the same BV category
(denominators: raw/R1_category_month_totals.csv). Numerators: raw/R1_reviews_owned.csv + raw/G1_reviews_dsg_tail.csv
+ raw/R7_reviews_monarch.csv, mapped to category ancestry from raw/G1_products_upc_dsg.jsonl.
RERUN: python G1_family_share.py
"""
import os, json
import pandas as pd

RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\PB_SCRAPE\raw"
P = pd.DataFrame([json.loads(l) for l in open(os.path.join(RAW, "G1_products_upc_dsg.jsonl"), encoding="utf-8")])
anc = {r.id: set(r.anc or []) | {r.cat} for r in P.itertuples()}
food = (P.brand == "Quest") & P.name.fillna("").str.contains("Protein|Bar\\b|Cookie|Nutrition|Chips|Shake", case=False)
excl = set(P[food].id)
cols = ["review_id", "product_id", "brand_id", "submission_time", "campaign_id", "is_syndicated"]
R = pd.concat([pd.read_csv(os.path.join(RAW, "R1_reviews_owned.csv"), usecols=cols, low_memory=False),
               pd.read_csv(os.path.join(RAW, "G1_reviews_dsg_tail.csv"), usecols=cols, low_memory=False)])
Rm = pd.read_csv(os.path.join(RAW, "R7_reviews_monarch.csv"), low_memory=False)
R = pd.concat([R, Rm[[c for c in cols if c in Rm.columns]]])
R = R[(R.campaign_id == "ESP_PIE_INCENTIVE") & (R.is_syndicated.astype(str) == "False") & ~R.product_id.isin(excl)]
R["mo"] = R.submission_time.str[5:7]; R["yr"] = R.submission_time.str[:4]
R = R[R.mo.isin(["04", "05", "06", "07", "08"]) & R.yr.isin(["2024", "2025", "2026"])]

C = pd.read_csv(os.path.join(RAW, "R1_category_month_totals.csv"), keep_default_na=False)
C = C.sort_values("pulled_at").drop_duplicates(["category", "month", "variant"], keep="last")
C = C[C.variant == "PIE"]; C["total"] = pd.to_numeric(C.total)
C["yr"] = C.month.str[:4]; C["mo"] = C.month.str[5:7]
C = C[C.mo.isin(["04", "05", "06", "07", "08"])]

BASKETS = {"FITNESS": ["ExerciseFitness-128988"], "OUTDOOR": ["CampingHiking-128904", "BikesCycling-128852"],
           "TEAM": ["ShopBySport-128771"], "GOLF": ["Golf-129239"], "GOLFBALLS": ["GolfBalls-129255"],
           "APPAREL": ["WomensApparel-129841", "MensApparel-129824", "BoysApparel-129859", "girls-apparel-footwear"]}
GROUPS = {"ETHOS": ["ETHOS"], "Fitness_Gear": ["Fitness_Gear"], "PRIMED": ["PRIMED"],
          "ETHOS+FG+PRIMED": ["ETHOS", "Fitness_Gear", "PRIMED"], "DSG": ["DSG"], "Quest": ["Quest"],
          "DSG+Quest": ["DSG", "Quest"], "Maxfli": ["Maxfli"], "Top_Flite": ["Top_Flite"], "Maxfli+TopFlite": ["Maxfli", "Top_Flite"],
          "tail(DBX,P-TEX,Jawbone,Slazenger,DICKS SG,TourTrek,Monarch)": ["DBX", "P-TEX", "Jawbone", "Slazenger", "DICK_S_Sporting_Goods", "Tour_Trek", "Monarch"],
          "X01 list": ["Calia", "CALIA_by_Carrie_Underwood", "VRST", "DSG", "Maxfli", "Walter_Hagen", "Lady_Hagen", "Alpine_Design",
                       "ETHOS", "Fitness_Gear", "Top_Flite", "Tommy_Armour_Golf", "Nishiki", "Quest", "PRIMED"]}
GROUPS["X01 list + tail"] = GROUPS["X01 list"] + GROUPS["tail(DBX,P-TEX,Jawbone,Slazenger,DICKS SG,TourTrek,Monarch)"]
rows = []
for b, cats in BASKETS.items():
    den = C[C.category.isin(cats)].groupby("yr").total.sum()
    inb = R[R.product_id.map(lambda i: bool(anc.get(i, set()) & set(cats)))]
    for gname, bs in GROUPS.items():
        num = inb[inb.brand_id.isin(bs)].drop_duplicates("review_id").groupby("yr").review_id.nunique()
        rows.append([b, gname] + [round(100 * num.get(y, 0) / den.get(y, float("nan")), 2) for y in ["2024", "2025", "2026"]]
                    + [int(num.get(y, 0)) for y in ["2024", "2025", "2026"]] + [int(den.get(y, 0)) for y in ["2024", "2025", "2026"]])
out = pd.DataFrame(rows, columns=["basket", "group", "sh24", "sh25", "sh26", "n24", "n25", "n26", "den24", "den25", "den26"])
out.to_csv(os.path.join(RAW, "G1_family_share_AprAug.csv"), index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 200)
print(out[(out.n26 + out.n25) > 0].to_string(index=False))
