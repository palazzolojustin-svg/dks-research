"""X01 analysis: owned-brand share of dicks.com reviews by category and month.

Inputs (from X01_bv_reviews.py and X01_bv_category_totals.py):
  raw/X01_products_dsg.csv, raw/X01_reviews_dsg.csv, raw/X01_category_month_totals_dsg.csv
Output: raw/X01_owned_share_by_category_month.csv and printed summary tables.
Numerator: unique native (non-syndicated) reviews on owned-brand products whose CURRENT BV category
ancestry contains the category (same definition BV uses for the CategoryAncestorId filter).
Denominator: all-brand native reviews in the same category-month (ALL) or post-purchase-email only (PIE).
RERUN: python X01_analyze.py
"""
import pandas as pd, os
RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\PB_SCRAPE\raw"
p = pd.read_csv(os.path.join(RAW, "X01_products_dsg.csv"))
r = pd.read_csv(os.path.join(RAW, "X01_reviews_dsg.csv"))
c = pd.read_csv(os.path.join(RAW, "X01_category_month_totals_dsg.csv"))
r = r[r.is_syndicated.astype(str) == "False"]
r["m"] = pd.to_datetime(r.submission_time, utc=True).dt.strftime("%Y-%m")
anc = p.set_index("product_id").ancestry.fillna("").str.split("|").to_dict()
rows = []
for cat in c.category.unique():
    pids = {k for k, v in anc.items() if cat in v}
    sub = r[r.product_id.isin(pids)]
    for var in ("ALL", "PIE"):
        s = sub if var == "ALL" else sub[sub.campaign_id == "ESP_PIE_INCENTIVE"]
        num = s.drop_duplicates("review_id").groupby("m").size()
        den = c[(c.category == cat) & (c.variant == var)].set_index("month").total
        for m, d in den.items():
            rows.append([cat, var, m, int(num.get(m, 0)), d])
out = pd.DataFrame(rows, columns=["category", "variant", "month", "owned", "total"])
out["share"] = out.owned / out.total
out.to_csv(os.path.join(RAW, "X01_owned_share_by_category_month.csv"), index=False)
pd.set_option("display.width", 400); pd.set_option("display.max_columns", 40)
for var in ("ALL", "PIE"):
    pv = out[out.variant == var].pivot_table(index="month", columns="category", values="share")
    print("=== owned share", var); print((pv * 100).round(1).to_string())


def window(df, months):
    d = df[df.month.isin(months)].groupby(["category", "variant"])[["owned", "total"]].sum()
    return d.owned / d.total


def ym(y, ms):
    return [f"{y}-{m:02d}" for m in ms]


summ = pd.DataFrame({
    "AprJul2024": window(out, ym(2024, range(4, 8))), "AprJul2025": window(out, ym(2025, range(4, 8))),
    "AprJul2026": window(out, ym(2026, range(4, 8))),
    "AugNov2025": window(out, ym(2025, range(8, 12))), "Jan-Mar2026": window(out, ym(2026, range(1, 4))),
    "FY23(Feb23-Jan24)": window(out, ym(2023, range(2, 13)) + ["2024-01"]),
    "FY24(Feb24-Jan25)": window(out, ym(2024, range(2, 13)) + ["2025-01"]),
    "FY25(Feb25-Jan26)": window(out, ym(2025, range(2, 13)) + ["2026-01"]),
    "FY26ytd(Feb-Jul26)": window(out, ym(2026, range(2, 8))),
    "FY25same(Feb-Jul25)": window(out, ym(2025, range(2, 8))),
}) * 100
print("=== window shares (%)"); print(summ.round(1).to_string())
summ.round(2).to_csv(os.path.join(RAW, "X01_owned_share_windows.csv"))
