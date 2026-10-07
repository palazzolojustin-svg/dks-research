"""G1: golf-ball MODEL review velocity on dicks.com/golfgalaxy (shared BV pool): Maxfli Tour X vs Pro V1 / TP5 / Chrome etc.
Reads raw/R1_reviews_owned.csv + raw/R1_reviews_national.csv with product names (raw/G1_products_upc_dsg.jsonl,
raw/R1_products_national.csv). Counts UNIQUE native review ids per model per month (all campaigns, and PIE-only),
restricted to golf-ball products (category ancestry contains GolfBalls).
Also reconstructs the card-label total for 'Maxfli Tour X Golf Balls' (24MAXUMXFLTRXWHTDGBL) as of 2025-08-14 and 2026-09-06.
OUT: raw/G1_golfball_model_month.csv ; prints window tables.
RERUN: python G1_golfball_velocity.py (after R1_weekly.py refresh)
"""
import os, re, json
import pandas as pd

RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\PB_SCRAPE\raw"
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 300)
P = pd.DataFrame([json.loads(l) for l in open(os.path.join(RAW, "G1_products_upc_dsg.jsonl"), encoding="utf-8")])
P["ancs"] = P.anc.map(lambda a: "|".join(a or [])) + "|" + P.cat.fillna("")
N = pd.read_csv(os.path.join(RAW, "R1_products_national.csv"), low_memory=False)
prod = pd.concat([P.rename(columns={"id": "product_id", "brand": "brand_id"})[["product_id", "brand_id", "name", "ancs"]],
                  N.assign(ancs=N.ancestry.fillna("") + "|" + N.category_id.fillna(""))[["product_id", "brand_id", "name", "ancs"]]]).drop_duplicates("product_id")
prod = prod[prod.ancs.str.contains("GolfBalls", na=False)]

MODELS = [  # (label, brand, regex on name, exclude regex)
    ("Maxfli Tour X (all)", "Maxfli", r"Tour X", r"Umbrella"),
    ("Maxfli Tour X-LS", "Maxfli", r"Tour X[- ]?LS", None),
    ("Maxfli Tour", "Maxfli", r"Tour (Golf|Max|Personal|Custom)|Tour Golf Balls|20\d\d Tour Golf|U/6 Tour Golf", r"Tour X|Tour S"),
    ("Maxfli Tour S", "Maxfli", r"Tour S\b", None),
    ("Maxfli all balls", "Maxfli", r".", None),
    ("Titleist Pro V1", "Titleist", r"Pro V1(?!x)", r"Pro V1x"),
    ("Titleist Pro V1x", "Titleist", r"Pro V1x", None),
    ("Titleist all balls", "Titleist", r".", None),
    ("TaylorMade TP5", "TaylorMade", r"TP5(?!x)", r"TP5x|TP5X"),
    ("TaylorMade TP5x", "TaylorMade", r"TP5x|TP5X", None),
    ("TaylorMade all balls", "TaylorMade", r".", None),
    ("Callaway Chrome (Soft/Tour)", "Callaway", r"Chrome", None),
    ("Callaway Supersoft", "Callaway", r"Supersoft|SuperSoft", None),
    ("Callaway all balls", "Callaway", r".", None),
    ("Srixon Z-Star", "Srixon", r"Z-STAR|Z-Star|ZSTAR", None),
    ("Bridgestone Tour B", "Bridgestone", r"Tour B", None),
]
cols = ["review_id", "product_id", "brand_id", "submission_time", "campaign_id", "is_syndicated"]
R = pd.concat([pd.read_csv(os.path.join(RAW, "R1_reviews_owned.csv"), usecols=cols, low_memory=False),
               pd.read_csv(os.path.join(RAW, "R1_reviews_national.csv"), usecols=cols, low_memory=False)])
R = R[R.product_id.isin(prod.product_id) & (R.is_syndicated.astype(str) == "False")]
R = R.merge(prod[["product_id", "name"]], on="product_id")
R["m"] = R.submission_time.str[:7]
rows = []
for lab, br, rx, ex in MODELS:
    s = R[(R.brand_id == br) & R.name.str.contains(rx, regex=True, na=False)]
    if ex:
        s = s[~s.name.str.contains(ex, regex=True, na=False)]
    s = s.drop_duplicates("review_id")
    for v, ss in [("ALL", s), ("PIE", s[s.campaign_id == "ESP_PIE_INCENTIVE"])]:
        c = ss.groupby("m").review_id.nunique()
        for m, n in c.items():
            rows.append([lab, v, m, n])
M = pd.DataFrame(rows, columns=["model", "variant", "month", "n"])
M.to_csv(os.path.join(RAW, "G1_golfball_model_month.csv"), index=False)


def win(months):
    return M[M.month.isin(months)].groupby(["model", "variant"]).n.sum().unstack("variant")


A25 = win([f"2025-{m:02d}" for m in range(4, 9)]); A26 = win([f"2026-{m:02d}" for m in range(4, 9)])
A24 = win([f"2024-{m:02d}" for m in range(4, 9)])
t = pd.concat({"AprAug24": A24, "AprAug25": A25, "AprAug26": A26}, axis=1).fillna(0).astype(int)
t["PIE_g25_26"] = (t[("AprAug26", "PIE")] / t[("AprAug25", "PIE")] - 1).round(3)
t["ALL_g25_26"] = (t[("AprAug26", "ALL")] / t[("AprAug25", "ALL")] - 1).round(3)
order = [m[0] for m in MODELS]
print("== native reviews, Apr-Aug windows (unique review ids; ALL campaigns and PIE-only)")
print(t.reindex(order).to_string())
# 13-month window matching X03's card labels: 2025-08-15 .. 2026-09-06
w = R[(R.submission_time >= "2025-08-15") & (R.submission_time < "2026-09-07")]
print("\n== native reviews added 2025-08-15..2026-09-06 (window of X03 card labels 57->813)")
for lab, br, rx, ex in MODELS:
    s = w[(w.brand_id == br) & w.name.str.contains(rx, regex=True, na=False)]
    if ex:
        s = s[~s.name.str.contains(ex, regex=True, na=False)]
    print(f"  {lab:30s} {s.review_id.nunique():6d}")
# card label reconstruction
tx = pd.read_csv(os.path.join(RAW, "R1_reviews_owned.csv"), low_memory=False)
tx = tx[tx.product_id == "24MAXUMXFLTRXWHTDGBL"]
print("\nTour X family product 24MAXUMXFLTRXWHTDGBL reviews in pull:", tx.review_id.nunique(),
      "syndicated:", (tx.is_syndicated.astype(str) == "True").sum())
for d in ["2024-12-31", "2025-08-14", "2025-12-31", "2026-04-30", "2026-09-06"]:
    print("   cumulative <=", d, (tx.submission_time <= d + "T23:59").sum())
print(tx.assign(m=tx.submission_time.str[:7]).groupby("m").review_id.nunique().to_string())
print(tx.campaign_id.fillna("NULL").value_counts().head(10).to_string())
