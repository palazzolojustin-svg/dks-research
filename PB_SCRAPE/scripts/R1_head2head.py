"""R1 (b): head-to-head review shares, owned brands vs named national brands, same BV category baskets and
the same all-brand denominators (raw/R1_category_month_totals.csv).
Inputs: X01 owned products/reviews, R1 national products/reviews (footwear-named products excluded for nationals).
Outputs: raw/R1_h2h_brand_month.csv (basket, brand, month, variant, n, total, share)
         raw/R1_h2h_windows.csv   (basket, brand, window, year, variant, n, total, share)
RERUN: python R1_head2head.py
"""
import os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
from R1_analyze import RAW, BASKETS, load_owned, campaign_type, denominators, fq

OWNED_GROUP = {"Calia": "CALIA", "CALIA_by_Carrie_Underwood": "CALIA", "DSG": "DSG", "VRST": "VRST",
               "Walter_Hagen": "Walter Hagen", "Lady_Hagen": "Walter Hagen", "Maxfli": "Maxfli", "Top_Flite": "Top-Flite",
               "Tommy_Armour_Golf": "Tommy Armour", "Alpine_Design": "Alpine Design", "ETHOS": "ETHOS",
               "Fitness_Gear": "Fitness Gear", "Nishiki": "Nishiki", "Quest": "Quest", "PRIMED": "PRIMED"}


def load_all():
    p, r = load_owned()
    r = r[["review_id", "product_id", "brand_id", "submission_time", "campaign_id"]].copy()
    r["grp"] = r.brand_id.map(OWNED_GROUP)
    r["owned"] = 1
    pn = pd.read_csv(os.path.join(RAW, "R1_products_national.csv"))
    rn = pd.read_csv(os.path.join(RAW, "R1_reviews_national.csv"), keep_default_na=False, na_values=[""],
                     usecols=["review_id", "product_id", "brand_id", "submission_time", "campaign_id", "is_syndicated"])
    rn = rn[rn.is_syndicated.astype(str) == "False"].drop(columns="is_syndicated")
    rn["grp"] = rn.brand_id.str.replace("_", " ")
    rn["owned"] = 0
    prod = pd.concat([p[["product_id", "ancestry"]], pn[["product_id", "ancestry"]]]).drop_duplicates("product_id")
    rev = pd.concat([r, rn], ignore_index=True)
    rev["m"] = rev.submission_time.str[:7]
    rev["typ"] = campaign_type(rev.campaign_id)
    return prod, rev


def main():
    prod, rev = load_all()
    den = denominators()
    anc = prod.set_index("product_id").ancestry.fillna("").str.split("|").to_dict()
    rows = []
    for b, cats in BASKETS.items():
        for cat in cats:
            pids = {k for k, v in anc.items() if cat in v}
            sub = rev[rev.product_id.isin(pids)].drop_duplicates("review_id")
            for var in ("PIE", "ORG", "ALL"):
                s = sub if var == "ALL" else sub[sub.typ == var]
                g = s.groupby(["grp", "m"]).size().rename("n").reset_index()
                g["owned_total"] = 0
                o = s[s.owned == 1].groupby("m").size().rename("n").reset_index(); o["grp"] = "ALL OWNED"
                g = pd.concat([g, o], ignore_index=True)
                g["basket"], g["category"], g["variant"] = b, cat, var
                rows.append(g)
    h = pd.concat(rows, ignore_index=True)
    h = h.groupby(["basket", "grp", "m", "variant"]).n.sum().reset_index()
    # PIE+ORG
    po = h[h.variant.isin(["PIE", "ORG"])].groupby(["basket", "grp", "m"]).n.sum().reset_index(); po["variant"] = "PIE+ORG"
    h = pd.concat([h, po], ignore_index=True)
    dd = []
    for b, cats in BASKETS.items():
        x = den[den.category.isin(cats)].groupby(["month", "variant"]).total.sum().reset_index()
        x["basket"] = b
        dd.append(x)
    dd = pd.concat(dd)
    pdn = dd[dd.variant.isin(["PIE", "ORG"])].groupby(["basket", "month"]).total.sum().reset_index(); pdn["variant"] = "PIE+ORG"
    dd = pd.concat([dd, pdn]).rename(columns={"month": "m"})
    h = h.merge(dd, on=["basket", "m", "variant"], how="left")
    h["share"] = h.n / h.total
    h["fq"] = h.m.map(fq)
    h.to_csv(os.path.join(RAW, "R1_h2h_brand_month.csv"), index=False)
    W = {"Apr-Aug": [4, 5, 6, 7, 8], "Feb-Jul": [2, 3, 4, 5, 6, 7], "Jun-Aug": [6, 7, 8], "Aug": [8]}
    out = []
    for wn, ms in W.items():
        for y in (2024, 2025, 2026):
            mm = [f"{y}-{m:02d}" for m in ms]
            s = h[h.m.isin(mm)]
            tot = dd[dd.m.isin(mm)].groupby(["basket", "variant"]).total.sum()
            g = s.groupby(["basket", "grp", "variant"]).n.sum().reset_index()
            g["total"] = [tot.get((a, v), np.nan) for a, v in zip(g.basket, g.variant)]
            g["window"], g["year"] = wn, y
            out.append(g)
    w = pd.concat(out, ignore_index=True)
    w["share"] = w.n / w.total
    w.to_csv(os.path.join(RAW, "R1_h2h_windows.csv"), index=False)
    return h, w


if __name__ == "__main__":
    h, w = main()
    pd.set_option("display.width", 250); pd.set_option("display.max_rows", 2000)
    for wn in ("Apr-Aug", "Feb-Jul"):
        x = w[(w.window == wn) & (w.variant == "PIE+ORG")].pivot_table(index=["basket", "grp"], columns="year", values="share") * 100
        x["d26v25"] = x[2026] - x[2025]
        n = w[(w.window == wn) & (w.variant == "PIE+ORG")].pivot_table(index=["basket", "grp"], columns="year", values="n")
        x["n26"] = n[2026]
        x = x[(x[2025] >= 1.0) | (x[2026] >= 1.0)]
        print("=====", wn, "PIE+ORG share of all-brand reviews in basket (%)")
        print(x.round(2).sort_values(["basket", 2026], ascending=[True, False]).to_string())
