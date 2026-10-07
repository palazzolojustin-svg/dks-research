"""R12: owned share of the first 24 default-sort ("Featured", selectedSort=5) slots, matched categories across periods.
Reads raw/R12_obs_long.csv (run R12_build_table.py first). Only archived captures (CC/Wayback) carry first-24 data;
the live census (X02) value is taken from raw/X02_dsg_products_20261007.csv sort='all' (=default Featured order) ranks 1-24.
Rerun: python PB_SCRAPE\\scripts\\R12_first24.py
"""
import os, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from R12_common import RAW
from R12_build_table import PERIODS, GROUP

d = pd.read_csv(os.path.join(RAW, "R12_obs_long.csv"), dtype={"d8": str})
d = d[(d.first24n == 24) & (d["sort"] == 5)]
# live first-24 from the X02 census (default sort, store 15108)
c = pd.read_csv(os.path.join(RAW, "X02_dsg_products_20261007.csv"))
c = c[(c["sort"] == "all") & (c["rank"] <= 24)]
live = c.groupby("cat").agg(first24=("vert", "sum"), first24n=("vert", "size")).reset_index().rename(columns={"cat": "slug"})
live["period"] = "LIVE"; live["d8"] = "20261007"; live["host"] = "dks"
d = pd.concat([d[["host", "slug", "d8", "period", "first24", "first24n"]], live[live.first24n == 24]], ignore_index=True)
tgt = {n: t for n, a, b, t in PERIODS}
d["dist"] = (pd.to_datetime(d.d8) - pd.to_datetime(d.period.map(tgt))).abs()
d = d.sort_values("dist").drop_duplicates(["host", "slug", "period"])
piv = d.pivot_table(index=["host", "slug"], columns="period", values="first24", aggfunc="first")
print(piv.to_string())
for a, b in [("25B", "LIVE"), ("25B", "26B"), ("24A", "25B"), ("23H2", "25B"), ("24A", "LIVE"), ("23H2", "LIVE")]:
    if a in piv and b in piv:
        m = piv[[a, b]].dropna()
        m = m[(m[a] > 0) | (m[b] > 0)]
        if len(m):
            print(f"{a}->{b}: n={len(m)} owned first-24 slots {int(m[a].sum())}/{24*len(m)} = {100*m[a].sum()/(24*len(m)):.1f}% -> "
                  f"{int(m[b].sum())} = {100*m[b].sum()/(24*len(m)):.1f}%  | cats up {(m[b]>m[a]).sum()} down {(m[b]<m[a]).sum()}")
