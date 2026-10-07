"""Q2 task 2 (analysis): Q3 FY26-to-date owned share of apparel reviews, DKS vs ASO, same calendar windows 2025 vs 2026.
Windows: A = Aug 1-17 (both DKS post-purchase-email batches present both years), B = Aug 18-Oct 6 (DKS email paused in 2026),
         C = Aug 1-Oct 6 (Q3 to date).
DKS: denominators Q2_dks_den_windows.csv (live BV counts, 2026-10-07), numerators Q2_dks_owned_reviews_recent.csv (fresh pull).
     Variants: ALL, PIE (post-purchase email), ORG (= NULL + MyAccount + BV display widgets), PIE+ORG.
ASO: PB_SCRAPE raw A1 review pull (2026-10-07 ~07:45 CDT) via A1_analyze.load() (read-only import). Variants ALLX/EMAIL/TEXT/PURCH/ORG.
Output Q2_q3td.csv ; printed table.  RERUN: python Q2_q3td.py
"""
import os, sys, math
import pandas as pd
sys.path.insert(0, r"C:\Users\palaz\Downloads\DKS_RESEARCH\PB_SCRAPE\scripts")
from A1_analyze import load as aso_load  # read-only

OUT = os.path.dirname(os.path.abspath(__file__))
WINS = {"A_Aug1-17": ("08-01", "08-18"), "B_Aug18-Oct6": ("08-18", "10-07"), "C_Aug1-Oct6": ("08-01", "10-07")}
APP = {"APPAREL": ["WomensApparel-129841", "MensApparel-129824", "BoysApparel-129859", "girls-apparel-footwear"],
       "MENS": ["MensApparel-129824"], "WOMENS": ["WomensApparel-129841"], "KIDS": ["BoysApparel-129859", "girls-apparel-footwear"]}
ORGC = {"MyAccount", "BV_REVIEW_DISPLAY", "BV_MOBILE_REVIEW_DISPLAY", ""}
rows = []
# ---- DKS ----
den = pd.read_csv(os.path.join(OUT, "Q2_dks_den_windows.csv"), keep_default_na=False)
den["total"] = pd.to_numeric(den.total)
rv = pd.read_csv(os.path.join(OUT, "Q2_dks_owned_reviews_recent.csv"), keep_default_na=False)
food = rv.brand_id.eq("Quest")
rv = rv[~food].drop_duplicates("review_id")
rv["md"] = rv.submission_time.str[5:10]; rv["y"] = rv.submission_time.str[:4].astype(int)
rv["typ"] = rv.campaign_id.map(lambda c: "PIE" if c == "ESP_PIE_INCENTIVE" else ("ORG" if c in ORGC else ("SAMP" if c.startswith("bvsampling") else "OTHER")))
for b, cats in APP.items():
    for wn, (a, z) in WINS.items():
        for y in (2025, 2026):
            dd = den[(den.category.isin(cats)) & (den.window == wn) & (den.year == y)].groupby("variant").total.sum()
            tot = {"ALL": dd["ALL"], "PIE": dd["PIE"], "ORG": dd["NULL"] + dd["MYACC"] + dd["BVDISP"] + dd["BVMOB"]}
            tot["PIE+ORG"] = tot["PIE"] + tot["ORG"]
            sub = rv[(rv.y == y) & (rv.md >= a) & (rv.md < z)]
            # each review counted once per category it sits under (same as R1: numerators by category ancestry)
            num = {"ALL": 0, "PIE": 0, "ORG": 0}
            for c in cats:
                s = sub[sub.ancestry.str.split("|").map(lambda L: c in L)]
                num["ALL"] += len(s); num["PIE"] += (s.typ == "PIE").sum(); num["ORG"] += (s.typ == "ORG").sum()
            num["PIE+ORG"] = num["PIE"] + num["ORG"]
            for v in tot:
                rows.append(("DKS", b, wn, y, v, int(num[v]), int(tot[v])))
# ---- ASO ----
A = pd.DataFrame(aso_load())
A["md"] = A.m.map("{:02d}".format) + "-" + A.d.map("{:02d}".format)
BK = {"APPAREL": {"mens", "womens", "boys", "girls", "kids_other"}, "MENS": {"mens"}, "WOMENS": {"womens"}, "KIDS": {"boys", "girls", "kids_other"}}
for b, s in BK.items():
    for wn, (a, z) in WINS.items():
        for y in (2025, 2026):
            sub = A[A.basket.isin(s) & (A.y == y) & (A.md >= a) & (A.md < z)]
            for v in ("ALLX", "EMAIL", "TEXT", "PURCH", "ORG"):
                ss = sub[sub.vars.map(lambda x: v in x)]
                rows.append(("ASO", b, wn, y, v, int(ss.owned.sum()), len(ss)))
R = pd.DataFrame(rows, columns=["co", "basket", "window", "year", "variant", "owned", "total"])
R["share"] = R.owned / R.total.where(R.total > 0)
R.to_csv(os.path.join(OUT, "Q2_q3td.csv"), index=False)
if __name__ == "__main__":
    pd.set_option("display.width", 250); pd.set_option("display.max_rows", 400)
    P = R.assign(s=(R.share * 100).round(1).astype(str) + " (" + R.total.astype(str) + ")")
    print(P.pivot_table(index=["basket", "window", "co", "variant"], columns="year", values="s", aggfunc="first").to_string())
    print("\nASO last review date in pull:", A.assign(dt=A.y.astype(str) + "-" + A.md).dt.max())
