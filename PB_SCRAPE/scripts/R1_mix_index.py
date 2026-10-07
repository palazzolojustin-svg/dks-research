"""R1 (c): implied owned-brand SALES-MIX INDEX from Bazaarvoice review shares (INFERENCE).

Method
 1. For each DKS fiscal quarter, owned share of reviews in an APPAREL basket (Women's+Men's+Boys+Girls) and a
    HARDLINES basket (Golf + Exercise/Fitness + Camping/Hiking + Bikes + ShopBySport/team), from
    raw/R1_share_category_month.csv. Variants: PIE, PIE+ORG, ALL. Two weightings: pooled (volume-weighted) and
    equal-weight-by-month (cancels the mid-2025 review-email step-up). Months with <30 reviews dropped from eqw.
 2. Fixed category weights = DICK'S-segment FY25 sales (M1, FL footwear 84%): apparel $4,398.4M, hardlines $5,048.3M.
    index_q = (wA*sA_q + wH*sH_q) / (wA*sA_base + wH*sH_base), base = FY24 (Feb-24..Jan-25) for annual,
    same quarter of FY24 for quarterly.
 3. Calibrate: owned-brand penetration of DICK'S non-footwear merch FY24 = 18.39% (M1 mid; band 18.02-18.77);
    implied penetration_t = 18.39 * index_t. Owned % of DICK'S sales assumes M1 fw 30.33% / other 3.4% (FY26)
    -> penetration * (1-0.3033-0.034).
 4. Back-test: FY23->FY24 and FY24->FY25 implied change vs the 10-K-derived bands (M1-1).
Output: raw/R1_mix_index.csv ; printed tables.  RERUN: python R1_mix_index.py (after R1_analyze.py)
"""
import os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
from R1_analyze import RAW, fq

APP = ["WomensApparel-129841", "MensApparel-129824", "BoysApparel-129859", "girls-apparel-footwear"]
HL = ["Golf-129239", "ExerciseFitness-128988", "CampingHiking-128904", "BikesCycling-128852", "ShopBySport-128771"]
WA, WH = 4398.4, 5048.3
BASE_PEN = 18.39
M1_BANDS = {"FY23": (17.56, 17.85), "FY24": (18.02, 18.77), "FY25": (18.67, 19.58)}

cm = pd.read_csv(os.path.join(RAW, "R1_share_category_month.csv"))
po = cm[cm.variant.isin(["PIE", "ORG"])].groupby(["category", "month"])[["owned", "total"]].sum().reset_index()
po["variant"] = "PIE+ORG"
cm = pd.concat([cm, po], ignore_index=True)
cm["fq"] = cm.month.map(fq)
cm["fy"] = cm.fq.str[:4]
cm["month_key"] = cm.month


def basket_share(cats, var, key):
    s = cm[(cm.category.isin(cats)) & (cm.variant == var)].groupby([key, "month"])[["owned", "total"]].sum().reset_index()
    s["share"] = s.owned / s.total.replace(0, np.nan)
    pooled = s.groupby(key).apply(lambda g: g.owned.sum() / g.total.sum())
    eqw = s[s.total >= 30].groupby(key).share.mean()
    n = s.groupby(key).total.sum()
    return pooled, eqw, n


rows = []
for key in ("fy", "fq", "month_key"):
    for var in ("PIE", "PIE+ORG", "ALL"):
        pa, ea, na = basket_share(APP, var, key)
        ph, eh, nh = basket_share(HL, var, key)
        for wt, A, H in (("pooled", pa, ph), ("eqw", ea, eh)):
            for per in A.index:
                rows.append((key, var, wt, per, A.get(per), H.get(per), na.get(per), nh.get(per)))
d = pd.DataFrame(rows, columns=["level", "variant", "weighting", "period", "app_share", "hl_share", "app_n", "hl_n"])
d["blend"] = (WA * d.app_share + WH * d.hl_share) / (WA + WH)


def base_of(r):
    if r.level == "fy":
        b = "FY24"
    elif r.level == "month_key":
        b = "2024" + r.period[4:]
    else:
        b = "FY24" + r.period[4:]
    m = d[(d.level == r.level) & (d.variant == r.variant) & (d.weighting == r.weighting) & (d.period == b)]
    return m.blend.iloc[0] if len(m) else np.nan


d["base_blend"] = d.apply(base_of, axis=1)
d["index_vs_FY24"] = 100 * d.blend / d.base_blend
d["implied_pen_nonfw"] = BASE_PEN * d.index_vs_FY24 / 100
d["implied_owned_pct_dk"] = d.implied_pen_nonfw * (1 - 0.3033 - 0.034)
# y/y index (same quarter / year a year earlier)
def prev(p):
    if p[:2] != "FY":
        return f"{int(p[:4]) - 1}{p[4:]}"
    return f"FY{int(p[2:4]) - 1:02d}{p[4:]}"
d["prev_blend"] = d.apply(lambda r: d[(d.level == r.level) & (d.variant == r.variant) & (d.weighting == r.weighting)
                                       & (d.period == prev(r.period))].blend.squeeze() if len(d[(d.level == r.level) & (d.variant == r.variant) & (d.weighting == r.weighting) & (d.period == prev(r.period))]) else np.nan, axis=1)
d["yoy_rel_pct"] = 100 * (d.blend / pd.to_numeric(d.prev_blend, errors="coerce") - 1)
d["app_yoy_pp"] = np.nan
d.to_csv(os.path.join(RAW, "R1_mix_index.csv"), index=False)

if __name__ == "__main__":
    pd.set_option("display.width", 250); pd.set_option("display.max_rows", 500)
    a = d[d.level == "fy"].copy()
    a[["app_share", "hl_share", "blend"]] *= 100
    print(a[["variant", "weighting", "period", "app_share", "hl_share", "blend", "index_vs_FY24", "implied_pen_nonfw", "yoy_rel_pct", "app_n", "hl_n"]].round(2).to_string())
    print("10-K/M1 penetration bands:", M1_BANDS, " implied FY23->FY24 / FY24->FY25 ratios vs band ratios:",
          {k: (round(M1_BANDS['FY24'][0] / M1_BANDS['FY23'][1], 3), round(M1_BANDS['FY24'][1] / M1_BANDS['FY23'][0], 3)) for k in ['23->24']},
          {k: (round(M1_BANDS['FY25'][0] / M1_BANDS['FY24'][1], 3), round(M1_BANDS['FY25'][1] / M1_BANDS['FY24'][0], 3)) for k in ['24->25']})
    q = d[(d.level == "fq") & (d.variant == "PIE+ORG")].copy()
    q[["app_share", "hl_share", "blend"]] *= 100
    print(q[["weighting", "period", "app_share", "hl_share", "blend", "index_vs_FY24", "implied_pen_nonfw", "implied_owned_pct_dk", "yoy_rel_pct", "app_n", "hl_n"]].round(2).to_string())


