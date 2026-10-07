"""G1: quantify how much DKS owned-brand review growth is relabelling (style moved from one brand to another).

Relabel link = new style (brand B, season s) is the successor of an older style (brand A != B, season < s) if:
  (1) shared UPC / BV FamilyId / shared review id (raw/G1_relabel_directional.csv), or
  (2) same brand-stripped normalized name AND same leaf category, where either the new style inherited review history
      (first review year <= season year - 2) or the old style was still alive within 2 years of the new season.
Origin brands searched: all DKS owned/exclusive brands (raw/G1_products_upc_dsg.jsonl) + 35 national brands
(raw/R1_products_national.csv) + licensed lines (raw/R7_products_licensed.csv).
Reviews: raw/R1_reviews_owned.csv + raw/G1_reviews_dsg_tail.csv + raw/R7_reviews_monarch.csv (PIE+ORG only).
Outputs raw/G1_relabel_links.csv, raw/G1_relabel_brand_windows.csv; prints the brand table.
RERUN: python G1_relabel_detect.py ; python G1_relabel_quantify.py
"""
import os, json, re
import pandas as pd

RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\PB_SCRAPE\raw"
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 500); pd.set_option("display.max_colwidth", 55)

X01_OWNED = {"Calia", "CALIA_by_Carrie_Underwood", "VRST", "DSG", "Maxfli", "Walter_Hagen", "Lady_Hagen", "Alpine_Design",
             "ETHOS", "Fitness_Gear", "Top_Flite", "Tommy_Armour_Golf", "Nishiki", "Quest", "PRIMED", "Field___Stream"}
BRANDWORDS = ["fitness gear", "ethos", "dick's sporting goods", "dicks sporting goods", "dsg", "quest", "alpine design",
              "top flite", "top-flite", "maxfli", "tommy armour", "walter hagen", "lady hagen", "calia by carrie underwood",
              "calia", "vrst", "nishiki", "primed", "field & stream", "monarch", "prince", "dbx", "p-tex", "jawbone",
              "slazenger", "tour trek", "under armour", "nike", "adidas", "callaway", "titleist", "taylormade", "wilson",
              "rawlings", "easton", "coleman", "yeti", "the north face", "columbia", "champion", "lotto", "cobra", "marucci",
              "™", "®"]


def norm(s):
    s = str(s).lower()
    for w in BRANDWORDS:
        s = s.replace(w, " ")
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def season(i):
    s = str(i)[:2]
    return 2000 + int(s) if s.isdigit() else None


# ---- product master
P = pd.DataFrame([json.loads(l) for l in open(os.path.join(RAW, "G1_products_upc_dsg.jsonl"), encoding="utf-8")])
P = P.rename(columns={"id": "product_id", "brand": "brand_id"})[["product_id", "brand_id", "name", "cat", "active", "total_reviews", "first_sub", "last_sub"]]
N = pd.read_csv(os.path.join(RAW, "R1_products_national.csv"), low_memory=False).rename(columns={"category_id": "cat"})
L = pd.read_csv(os.path.join(RAW, "R7_products_licensed.csv"), low_memory=False)
L = L.rename(columns={c: c for c in L.columns})
if "category_id" in L.columns:
    L = L.rename(columns={"category_id": "cat"})
cols = ["product_id", "brand_id", "name", "cat", "active", "total_reviews", "first_sub", "last_sub"]
ALL = pd.concat([P[cols], N[cols], L[[c for c in cols if c in L.columns]]], ignore_index=True).drop_duplicates("product_id")
ALL["season"] = ALL.product_id.map(season)
ALL["key"] = ALL.name.map(norm)
ALL["first_year"] = pd.to_numeric(ALL.first_sub.str[:4], errors="coerce")
ALL["last_year"] = pd.to_numeric(ALL.last_sub.str[:4], errors="coerce")
owned_like = set(P.brand_id)

# ---- links (2): name + category
new = ALL[ALL.brand_id.isin(owned_like) & ALL.season.notna()]
old = ALL[ALL.season.notna()]
m = new.merge(old, on=["key", "cat"], suffixes=("", "_o"))
m = m[(m.brand_id != m.brand_id_o) & (m.season_o < m.season) & (m.key.str.split().str.len() >= 2)]
inherited = m.first_year <= (m.season - 2)
alive = m.last_year_o.fillna(m.season_o) >= (m.season - 2)
m = m[inherited | alive]
m["method"] = "name+cat"
links = m[["product_id", "brand_id", "season", "name", "cat", "product_id_o", "brand_id_o", "season_o", "name_o", "method"]]
# ---- links (1): definitive
dd = pd.read_csv(os.path.join(RAW, "G1_relabel_directional.csv"))
dd = dd.rename(columns={"new_id": "product_id", "new_brand": "brand_id", "new_season": "season", "old_id": "product_id_o",
                        "old_brand": "brand_id_o", "old_season": "season_o"})
nm = dict(zip(ALL.product_id, ALL.name)); ct = dict(zip(ALL.product_id, ALL.cat))
dd["name"] = dd.product_id.map(nm); dd["name_o"] = dd.product_id_o.map(nm); dd["cat"] = dd.product_id.map(ct)
dd["season"] = dd.season + 2000; dd["season_o"] = dd.season_o + 2000
links = pd.concat([links, dd[links.columns]], ignore_index=True)
# keep first origin per new product (prefer definitive)
links["prio"] = (links.method == "name+cat").astype(int)
links = links.sort_values(["product_id", "prio", "season_o"], ascending=[True, True, False]).drop_duplicates("product_id")
# drop DSG<->CALIA-type generic apparel name collisions unless inherited/definitive: flag apparel
links["apparel"] = links.cat.fillna("").str.contains("Womens|Mens|Boys|Girls|Shirt|Pant|Short|Jacket|Hood|Bra|Legging|Tank|Dress|Skirt|Skort|Polo|Sweat|Jogger|Fleece|Hat|Beanie|Sock|Swim", case=False)
links.to_csv(os.path.join(RAW, "G1_relabel_links.csv"), index=False)
print("== relabel links (new owned/exclusive style <- older style of another brand)")
print(links.groupby(["brand_id_o", "brand_id", "apparel"]).agg(n=("product_id", "size"), seasons=("season", lambda s: f"{int(s.min())}-{int(s.max())}")).sort_values("n", ascending=False).head(60).to_string())

# ---- reviews
cols_r = ["review_id", "product_id", "brand_id", "submission_time", "campaign_id"]
R = pd.concat([pd.read_csv(os.path.join(RAW, "R1_reviews_owned.csv"), usecols=cols_r, low_memory=False),
               pd.read_csv(os.path.join(RAW, "G1_reviews_dsg_tail.csv"), usecols=cols_r, low_memory=False)], ignore_index=True)
try:
    Rm = pd.read_csv(os.path.join(RAW, "R7_reviews_monarch.csv"), low_memory=False)
    Rm = Rm[[c for c in cols_r if c in Rm.columns]]
    R = pd.concat([R, Rm], ignore_index=True)
except Exception as ex:
    print("monarch reviews not loaded", ex)
R["camp"] = R.campaign_id.fillna("NULL")
R = R[R.camp.isin(["ESP_PIE_INCENTIVE", "NULL", "MyAccount", "BV_REVIEW_DISPLAY", "BV_MOBILE_REVIEW_DISPLAY"])]
R = R.drop_duplicates(["review_id", "brand_id"])
R["ym"] = R.submission_time.str[:7]
R["mo"] = R.submission_time.str[5:7]
R["yr"] = R.submission_time.str[:4]
W = R[R.mo.isin(["04", "05", "06", "07", "08"]) & R.yr.isin(["2024", "2025", "2026"])]
lk = links.set_index("product_id")
W = W.join(lk[["brand_id_o", "apparel"]], on="product_id")
W["relabel_in"] = W.brand_id_o.notna()
tab = W.groupby(["brand_id", "yr"]).agg(all=("review_id", "nunique"), relabel=("relabel_in", "sum")).unstack("yr").fillna(0)
tab.columns = [f"{a}_{b}" for a, b in tab.columns]
tab["g_all_25_26"] = tab.all_2026 / tab.all_2025 - 1
tab["g_native_25_26"] = (tab.all_2026 - tab.relabel_2026) / (tab.all_2025 - tab.relabel_2025) - 1
tab["g_all_24_26"] = tab.all_2026 / tab.all_2024 - 1
tab["g_native_24_26"] = (tab.all_2026 - tab.relabel_2026) / (tab.all_2024 - tab.relabel_2024) - 1
tab["relabel_share_2026"] = tab.relabel_2026 / tab.all_2026
tab.to_csv(os.path.join(RAW, "G1_relabel_brand_windows.csv"))
print("\n== Apr-Aug PIE+ORG reviews by brand; 'relabel' = reviews on styles that are successors of another brand's style")
print(tab.round(3).sort_values("all_2026", ascending=False).to_string())

# origin breakdown of relabel reviews 2026 and 2024
print("\n== relabel-in reviews by origin -> brand, Apr-Aug")
print(W[W.relabel_in].groupby(["brand_id_o", "brand_id", "yr"]).review_id.nunique().unstack("yr").fillna(0).astype(int).sort_values("2026", ascending=False).head(40).to_string())

# group-level (combined families) growth
groups = {"ETHOS+Fitness_Gear+PRIMED": ["ETHOS", "Fitness_Gear", "PRIMED"], "DSG+Quest+DBX+DICK'S SG": ["DSG", "Quest", "DBX", "DICK_S_Sporting_Goods"],
          "Maxfli+Top_Flite": ["Maxfli", "Top_Flite"], "Walter_Hagen+Lady_Hagen": ["Walter_Hagen", "Lady_Hagen"],
          "Monarch+Prince": ["Monarch", "Prince"], "X01 owned list": sorted(X01_OWNED),
          "X01 owned + exclusive tail": sorted(X01_OWNED | {"DBX", "P-TEX", "Jawbone", "Slazenger", "DICK_S_Sporting_Goods", "Tour_Trek", "Monarch"})}
print("\n== group totals Apr-Aug PIE+ORG reviews (2024, 2025, 2026)")
for gname, bs in groups.items():
    s = W[W.brand_id.isin(bs)].drop_duplicates("review_id").groupby("yr").review_id.nunique()
    print(f"{gname:32s}", [int(s.get(y, 0)) for y in ["2024", "2025", "2026"]], f"g25-26 {s.get('2026',0)/max(s.get('2025',1),1)-1:+.1%}  g24-26 {s.get('2026',0)/max(s.get('2024',1),1)-1:+.1%}")
for b in ["ETHOS", "Fitness_Gear", "PRIMED", "DSG", "Quest", "DBX", "DICK_S_Sporting_Goods", "Maxfli", "Top_Flite", "Monarch", "Prince", "Walter_Hagen", "Lady_Hagen", "Slazenger", "P-TEX", "Jawbone", "Calia", "VRST"]:
    s = W[W.brand_id == b].groupby("yr").review_id.nunique()
    print(f"   {b:28s}", [int(s.get(y, 0)) for y in ["2024", "2025", "2026"]])
