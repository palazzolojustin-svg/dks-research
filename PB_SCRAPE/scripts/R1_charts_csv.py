"""R1: write charts-ready CSVs.
 raw/R1_chart_owned_share_month.csv : month, fiscal_quarter, basket, owned_share_all, owned_share_pie,
                                      owned_share_organic, owned_share_pie_plus_organic, n_all, n_pie, n_organic
 raw/R1_chart_h2h_fq.csv            : fiscal_quarter, basket, brand, share_pie_plus_organic, n
Run after R1_analyze.py and R1_head2head.py.  RERUN: python R1_charts_csv.py
"""
import os, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
from R1_analyze import RAW, fq

b = pd.read_csv(os.path.join(RAW, "R1_share_basket_month.csv"))
b["owned_share_pie_plus_organic"] = (b.owned_PIE + b.owned_ORG) / (b.total_PIE + b.total_ORG)
b["fiscal_quarter"] = b.month.map(fq)
out = b[["month", "fiscal_quarter", "basket", "owned_share_all", "owned_share_pie", "owned_share_organic",
         "owned_share_pie_plus_organic", "total_ALL", "total_PIE", "total_ORG"]].rename(
    columns={"total_ALL": "n_all", "total_PIE": "n_pie", "total_ORG": "n_organic"})
out.to_csv(os.path.join(RAW, "R1_chart_owned_share_month.csv"), index=False)

h = pd.read_csv(os.path.join(RAW, "R1_h2h_brand_month.csv"))
h = h[h.variant == "PIE+ORG"]
n = h.groupby(["basket", "grp", "fq"]).n.sum()
tot = h.drop_duplicates(["basket", "m"]).groupby(["basket", "fq"]).total.sum()
g = n.reset_index()
g["total"] = [tot.get((a, q)) for a, q in zip(g.basket, g.fq)]
g["share_pie_plus_organic"] = g.n / g.total
g.rename(columns={"fq": "fiscal_quarter", "grp": "brand"}).to_csv(os.path.join(RAW, "R1_chart_h2h_fq.csv"), index=False)
print("ok", len(out), len(g))
