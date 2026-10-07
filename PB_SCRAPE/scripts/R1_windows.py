"""R1: window comparisons (same calendar months y/y) with standard errors, for variants PIE, ORG, PIE+ORG,
NULL-only organic, and equal-weight within-month shares. Reads raw/R1_share_category_month.csv (from R1_analyze.py)
plus raw/R1_category_month_totals.csv for the NULL-only denominator.
Output: raw/R1_windows.csv ; printed table.
RERUN: python R1_windows.py
"""
import os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
from R1_analyze import BASKETS, RAW, load_owned, campaign_type

cm = pd.read_csv(os.path.join(RAW, "R1_share_category_month.csv"))
# NULL-only organic numerators/denominators
p, r = load_owned()
r["m"] = r.submission_time.str[:7]
r["camp"] = r.campaign_id.fillna("__NULL__")
anc = p.set_index("product_id").ancestry.fillna("").str.split("|").to_dict()
den = pd.read_csv(os.path.join(RAW, "R1_category_month_totals.csv"), keep_default_na=False)
den = den.sort_values("pulled_at").drop_duplicates(["category", "month", "variant"], keep="last")
den["total"] = pd.to_numeric(den.total)
extra = []
for cat in sorted(set(sum(BASKETS.values(), []))):
    pids = {k for k, v in anc.items() if cat in v}
    sub = r[r.product_id.isin(pids)].drop_duplicates("review_id")
    g = sub[sub.camp == "__NULL__"].groupby("m").size()
    d = den[(den.category == cat) & (den.variant == "NULL")].set_index("month").total
    for m, t in d.items():
        extra.append((cat, m, "NULLONLY", int(g.get(m, 0)), t))
cm = pd.concat([cm, pd.DataFrame(extra, columns=["category", "month", "variant", "owned", "total"])], ignore_index=True)
# PIE+ORG combined (excludes sampling and misc campaigns)
po = cm[cm.variant.isin(["PIE", "ORG"])].groupby(["category", "month"])[["owned", "total"]].sum().reset_index()
po["variant"] = "PIE+ORG"
cm = pd.concat([cm, po], ignore_index=True)

WINDOWS = {"Feb-Jul": [2, 3, 4, 5, 6, 7], "Apr-Aug": [4, 5, 6, 7, 8], "Aug1-15proxy(Aug)": [8], "Feb-Apr(Q1)": [2, 3, 4],
           "May-Jul(Q2)": [5, 6, 7]}
out = []
for b, cats in BASKETS.items():
    s = cm[cm.category.isin(cats)].groupby(["variant", "month"])[["owned", "total"]].sum().reset_index()
    s["share"] = s.owned / s.total.replace(0, np.nan)
    for wn, ms in WINDOWS.items():
        for y in (2024, 2025, 2026):
            mm = [f"{y}-{m:02d}" for m in ms]
            for v, g in s[s.month.isin(mm)].groupby("variant"):
                o, t = g.owned.sum(), g.total.sum()
                sh = o / t if t else np.nan
                se = np.sqrt(sh * (1 - sh) / t) if t else np.nan
                ok = g[g.total >= 30]
                out.append((b, wn, y, v, int(o), int(t), sh, se, ok.share.mean() if len(ok) else np.nan))
w = pd.DataFrame(out, columns=["basket", "window", "year", "variant", "owned", "total", "pooled", "se", "eqw_month"])
w.to_csv(os.path.join(RAW, "R1_windows.csv"), index=False)
if __name__ == "__main__":
    pd.set_option("display.width", 250); pd.set_option("display.max_rows", 1000)
    for wn in ("Feb-Jul", "Apr-Aug"):
        t = w[w.window == wn].pivot_table(index=["basket", "variant"], columns="year", values=["pooled", "eqw_month"]) * 100
        t2 = w[w.window == wn].pivot_table(index=["basket", "variant"], columns="year", values=["total", "se"])
        t[("d26v25", "pooled")] = t[("pooled", 2026)] - t[("pooled", 2025)]
        t[("z", "")] = (w[(w.window == wn) & (w.year == 2026)].set_index(["basket", "variant"]).pooled -
                        w[(w.window == wn) & (w.year == 2025)].set_index(["basket", "variant"]).pooled) / np.sqrt(
            w[(w.window == wn) & (w.year == 2026)].set_index(["basket", "variant"]).se ** 2 +
            w[(w.window == wn) & (w.year == 2025)].set_index(["basket", "variant"]).se ** 2)
        print("=====", wn); print(pd.concat([t.round(1), t2[[("total", 2025), ("total", 2026)]]], axis=1).to_string())
