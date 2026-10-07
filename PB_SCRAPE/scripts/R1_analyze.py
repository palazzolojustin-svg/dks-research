"""R1 analysis: robust owned-brand review share on dicks.com (Bazaarvoice), extends X01.

Inputs
  raw/X01_products_dsg.csv, raw/X01_reviews_dsg.csv            owned-brand products + reviews (X01, 2026-10-07)
  raw/R1_category_month_totals.csv                               all-brand category-month totals by variant (R1)
  raw/R1_products_national.csv, raw/R1_reviews_national.csv     named national-brand reviews (R1)
Outputs
  raw/R1_share_category_month.csv   category x month x variant: owned, total, share   (charts-ready)
  raw/R1_share_basket_month.csv     basket x month: owned_share_all / _pie / _organic, equal-weight variants
  raw/R1_share_basket_fq.csv        basket x fiscal quarter, pooled and within-month (equal-weight) shares
  printed tables
Variants: ALL (all native), PIE (post-purchase incentive email), ORG (organic = no campaign / MyAccount /
BV display widgets; no incentive, no sampling), NONPIE.
Owned set = 10-K owned brands (+ Lady Hagen, CALIA by Carrie Underwood, PRIMED); EXCLUDES Field & Stream (exited)
and Quest Nutrition food items mis-branded as "Quest".
RERUN: python R1_analyze.py
"""
import os, re
import numpy as np
import pandas as pd

RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\PB_SCRAPE\raw"
ORG_CAMPS = {"__NULL__", "MyAccount", "BV_REVIEW_DISPLAY", "BV_MOBILE_REVIEW_DISPLAY"}
BASKETS = {
    "APPAREL": ["WomensApparel-129841", "MensApparel-129824", "BoysApparel-129859", "girls-apparel-footwear"],
    "WOMENS": ["WomensApparel-129841"], "MENS": ["MensApparel-129824"],
    "KIDS": ["BoysApparel-129859", "girls-apparel-footwear"],
    "GOLF": ["Golf-129239"], "GOLFBALLS": ["GolfBalls-129255"], "GOLFCLUBS": ["GolfClubs-132413"],
    "FITNESS": ["ExerciseFitness-128988"], "OUTDOOR": ["CampingHiking-128904", "BikesCycling-128852"],
    "TEAM": ["ShopBySport-128771"],
}


def fq(m):
    """CY month 'YYYY-MM' -> DKS fiscal quarter label (Q1 Feb-Apr, Q2 May-Jul, Q3 Aug-Oct, Q4 Nov-Jan)."""
    y, mo = int(m[:4]), int(m[5:7])
    fy = y - 1 if mo == 1 else y
    q = {2: 1, 3: 1, 4: 1, 5: 2, 6: 2, 7: 2, 8: 3, 9: 3, 10: 3, 11: 4, 12: 4, 1: 4}[mo]
    return f"FY{str(fy)[2:]}Q{q}"


def load_owned():
    p = pd.read_csv(os.path.join(RAW, "X01_products_dsg.csv"))
    food = (p.brand_id == "Quest") & p.name.fillna("").str.contains("Protein|Bar\\b|Cookie|Nutrition|Chips|Shake", case=False)
    p = p[(p.brand_id != "Field___Stream") & ~food]
    r = pd.read_csv(os.path.join(RAW, "X01_reviews_dsg.csv"), keep_default_na=False, na_values=[""])
    r = r[(r.is_syndicated.astype(str) == "False") & r.product_id.isin(p.product_id)]
    return p, r


def campaign_type(c):
    c = c.fillna("__NULL__")
    return np.select([c == "ESP_PIE_INCENTIVE", c.isin(ORG_CAMPS), c.str.startswith("bvsampling")], ["PIE", "ORG", "SAMP"], "OTHER")


def denominators():
    c = pd.read_csv(os.path.join(RAW, "R1_category_month_totals.csv"), keep_default_na=False)
    c = c.sort_values("pulled_at").drop_duplicates(["category", "month", "variant"], keep="last")
    c["total"] = pd.to_numeric(c.total)
    pv = c.pivot_table(index=["category", "month"], columns="variant", values="total", aggfunc="last").fillna(0)
    pv["ORG"] = pv["NULL"] + pv["MYACC"] + pv["BVDISP"] + pv["BVMOB"]
    return pv[["ALL", "PIE", "ORG", "NONPIE"]].stack().rename("total").reset_index().rename(columns={"level_2": "variant"})


def numerators(prod, rev, label="owned"):
    rev = rev.copy()
    rev["m"] = rev.submission_time.str[:7]
    rev["typ"] = campaign_type(rev.campaign_id)
    anc = prod.set_index("product_id").ancestry.fillna("").str.split("|").to_dict()
    out = []
    for cat in sum(BASKETS.values(), []):
        if cat in [o[0] for o in out]:
            pass
        pids = {k for k, v in anc.items() if cat in v}
        sub = rev[rev.product_id.isin(pids)].drop_duplicates("review_id")
        for var in ("ALL", "PIE", "ORG", "NONPIE"):
            s = sub if var == "ALL" else (sub[sub.typ != "PIE"] if var == "NONPIE" else sub[sub.typ == var])
            g = s.groupby("m").size()
            for m, n in g.items():
                out.append((cat, m, var, n))
    d = pd.DataFrame(out, columns=["category", "month", "variant", label]).drop_duplicates(["category", "month", "variant"])
    return d


def main():
    p, r = load_owned()
    den = denominators()
    num = numerators(p, r)
    cm = den.merge(num, on=["category", "month", "variant"], how="left").fillna({"owned": 0})
    cm["share"] = cm.owned / cm.total.replace(0, np.nan)
    cm["fq"] = cm.month.map(fq)
    cm.to_csv(os.path.join(RAW, "R1_share_category_month.csv"), index=False)

    rows = []
    for b, cats in BASKETS.items():
        s = cm[cm.category.isin(cats)].groupby(["month", "variant"])[["owned", "total"]].sum().reset_index()
        s["basket"] = b
        rows.append(s)
    bm = pd.concat(rows)
    bm["share"] = bm.owned / bm.total.replace(0, np.nan)
    bm["fq"] = bm.month.map(fq)
    wide = bm.pivot_table(index=["basket", "month"], columns="variant", values=["share", "owned", "total"]).reset_index()
    wide.columns = ["_".join([c for c in col if c]) for col in wide.columns]
    wide = wide.rename(columns={"share_ALL": "owned_share_all", "share_PIE": "owned_share_pie", "share_ORG": "owned_share_organic",
                                "share_NONPIE": "owned_share_nonpie"})
    wide.to_csv(os.path.join(RAW, "R1_share_basket_month.csv"), index=False)

    # fiscal-quarter: pooled (volume-weighted) and equal-weight-by-month (within-month share, volume step-up cancels)
    # Equal-weight months: drop months with total < 30 (Dec blackout / post-2026-08-16 pause) for PIE/ALL.
    def agg(g):
        pooled = g.owned.sum() / g.total.sum() if g.total.sum() else np.nan
        ok = g[g.total >= 30]
        ew = ok.share.mean() if len(ok) else np.nan
        return pd.Series({"owned": g.owned.sum(), "total": g.total.sum(), "pooled": pooled, "eqw_month": ew, "n_months": len(ok)})
    fqt = bm.groupby(["basket", "variant", "fq"]).apply(agg).reset_index()
    fqt.to_csv(os.path.join(RAW, "R1_share_basket_fq.csv"), index=False)
    return cm, bm, fqt


if __name__ == "__main__":
    cm, bm, fqt = main()
    pd.set_option("display.width", 250); pd.set_option("display.max_rows", 500)
    for var in ("PIE", "ORG", "ALL"):
        t = fqt[fqt.variant == var].pivot_table(index="fq", columns="basket", values="pooled") * 100
        print("=== pooled owned share by FQ,", var); print(t.round(1).to_string())
    t = fqt[fqt.variant == "ORG"].pivot_table(index="fq", columns="basket", values="owned")
    print("=== ORG owned n"); print(t.to_string())
    t = fqt[fqt.variant == "ORG"].pivot_table(index="fq", columns="basket", values="total")
    print("=== ORG total n"); print(t.to_string())
