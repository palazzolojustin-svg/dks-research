"""R7 analysis: licensed vs owned review volume inside DKS "vertical brands" (dicks.com Bazaarvoice reviews).

Inputs : raw/X01_reviews_dsg.csv (owned brands, from X01), raw/R7_reviews_licensed.csv + raw/R7_products_licensed_typed.csv
         (licensed brands, from R7_bv_licensed.py), raw/R7_reviews_monarch.csv (owned Monarch, not in X01's list).
Output : raw/R7_licensed_vs_owned_reviews.csv (window x line x variant counts) and printed tables.
Scopes (INFERENCE about what each licence covers):
  narrow : Lotto all; Prince all; adidas Football all; adidas Baseball all; Cobra complete sets only;
           Marucci apparel/accessories only (excl. bats and fielding gloves)
  broad  : as narrow but ALL Cobra and ALL Marucci products sold on dicks.com (upper bound; includes national-brand
           wholesale bats/clubs that are almost certainly NOT licensed)
Variants: ALL native (non-syndicated) reviews; PIE = CampaignId ESP_PIE_INCENTIVE (purchase-triggered).
RERUN  : python R7_analyze.py   (after R7_bv_licensed.py products/reviews and X01_bv_reviews.py)
"""
import os
import pandas as pd

RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\PB_SCRAPE\raw"
o = pd.read_csv(os.path.join(RAW, "X01_reviews_dsg.csv"), dtype=str)
o = o[o.owned == "1"].drop_duplicates("review_id")
m = pd.read_csv(os.path.join(RAW, "R7_reviews_monarch.csv"), dtype=str).drop_duplicates("review_id")
l = pd.read_csv(os.path.join(RAW, "R7_reviews_licensed.csv"), dtype=str).drop_duplicates("review_id")
p = pd.read_csv(os.path.join(RAW, "R7_products_licensed_typed.csv"), dtype=str)
l = l.merge(p[["product_id", "pull", "typ"]], on="product_id", how="left")


def line(r):
    pull, typ = r["pull"], r["typ"]
    if pull == "Cobra":
        return "Cobra sets" if typ == "set" else "Cobra other (clubs etc.)"
    if pull == "Marucci":
        if typ in ("bat", "glove_mitt"):
            return "Marucci bats/fielding gloves"
        return "Marucci apparel/accessories"
    if pull and pull.startswith("adidas|"):
        return "adidas " + pull.split("|")[1].split("-")[0]
    return pull


l["line"] = l.apply(line, axis=1)
NARROW = {"Lotto", "Prince", "adidas Football", "adidas Baseball", "Cobra sets", "Marucci apparel/accessories"}
BROAD_EXTRA = {"Cobra other (clubs etc.)", "Marucci bats/fielding gloves"}
o["line"] = "OWNED (X01 list)"
m["line"] = "OWNED Monarch"
cols = ["review_id", "submission_time", "is_syndicated", "campaign_id", "line"]
a = pd.concat([o[cols], m[cols], l[cols]])
a = a[a.is_syndicated.str.lower() != "true"]
a["dt"] = pd.to_datetime(a.submission_time.str[:10], errors="coerce")
a["pie"] = a.campaign_id == "ESP_PIE_INCENTIVE"
a["mo"] = a.dt.dt.month
a["yr"] = a.dt.dt.year


def win(r):
    if 4 <= r.mo <= 8:
        return f"AprAug{r.yr}"
    return None


a["win"] = a.apply(win, axis=1)
out = []
for var, sub in (("ALL", a), ("PIE", a[a.pie])):
    for key, g in list(sub.groupby("yr")) + list(sub.dropna(subset=["win"]).groupby("win")):
        c = g.line.value_counts()
        own = c.get("OWNED (X01 list)", 0) + c.get("OWNED Monarch", 0)
        nar = sum(c.get(x, 0) for x in NARROW)
        brd = nar + sum(c.get(x, 0) for x in BROAD_EXTRA)
        row = {"variant": var, "period": str(key), "owned": own, "licensed_narrow": nar, "licensed_broad": brd,
               "lic_share_narrow": round(nar / (own + nar), 4) if own + nar else None,
               "lic_share_broad": round(brd / (own + brd), 4) if own + brd else None}
        for x in sorted(NARROW | BROAD_EXTRA | {"OWNED Monarch"}):
            row[x] = c.get(x, 0)
        out.append(row)
df = pd.DataFrame(out)
df.to_csv(os.path.join(RAW, "R7_licensed_vs_owned_reviews.csv"), index=False)
pd.set_option("display.width", 300); pd.set_option("display.max_columns", 30)
print(df.to_string())

# ---- $-weighted licensed share (INFERENCE; appended 2026-10-07) ----
ASP = {"Lotto": 40, "Marucci apparel/accessories": 35, "adidas Football": 30, "adidas Baseball": 30, "Prince": 80,
       "Cobra sets": 600, "Cobra other (clubs etc.)": 300, "Marucci bats/fielding gloves": 150}
OWNED_ASP = {"central": 41, "low_lic": 73, "high_lic": 41}   # owned review-weighted offer $41 / list $73 (X02 census)
LIC_MULT = {"central": 1.0, "low_lic": 0.75, "high_lic": 1.5}
VERT = {2023: 1.6, 2024: 1.7, 2025: 1.8}   # 10-K vertical $B (FY23-FY25; calendar yr ~ fiscal yr)
rows = []
for _, r in df[df.variant == "PIE"].iterrows():
    for case in OWNED_ASP:
        nar = sum(r[k] * ASP[k] for k in NARROW) * LIC_MULT[case]
        brd = nar + sum(r[k] * ASP[k] for k in BROAD_EXTRA) * LIC_MULT[case]
        own = r["owned"] * OWNED_ASP[case]
        yr = int(r["period"][-4:]) if r["period"][-4:].isdigit() else None
        sh_n, sh_b = nar / (nar + own), brd / (brd + own)
        rows.append({"period": r["period"], "case": case, "lic_dollar_share_narrow": round(sh_n, 4),
                     "lic_dollar_share_broad": round(sh_b, 4),
                     "implied_licensed_$M_narrow": round(sh_n * VERT[yr] * 1000) if r["period"].isdigit() and yr in VERT else None,
                     "implied_owned_only_$B_narrow": round((1 - sh_n) * VERT[yr], 3) if r["period"].isdigit() and yr in VERT else None})
dd = pd.DataFrame(rows)
dd.to_csv(os.path.join(RAW, "R7_licensed_dollar_share.csv"), index=False)
print(dd.to_string())
