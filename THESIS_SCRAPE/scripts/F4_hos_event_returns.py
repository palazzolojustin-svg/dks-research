"""F4: DKS abnormal returns (vs XRT and ASO) around non-earnings House of Sport events.
Rerun: python THESIS_SCRAPE\\scripts\\F4_hos_event_returns.py  -> THESIS_SCRAPE\\raw\\F4_hos_event_returns.csv
Data: CORE_NOTES\\data\\peer_daily_closes_2021-2026-10-05.csv (Yahoo adj closes).
Events are dates with HoS-specific news and no DKS earnings print that day (dates from C05/C06R1/digest).
"""
import os, pandas as pd
base = os.path.join(os.path.dirname(__file__), "..", "..", "CORE_NOTES", "data")
p = pd.read_csv(os.path.join(base, "peer_daily_closes_2021-2026-10-05.csv"))
p = p.rename(columns={p.columns[0]: "date"})
p["date"] = pd.to_datetime(p["date"].astype(str).str[:10]); p = p.set_index("date").sort_index()
r = p[["DKS", "XRT", "ASO", "SPY"]].pct_change()
events = {
    "2025-09-18 HoS Jersey City grand opening + mgmt tour": "2025-09-18",
    "2025-09-19 Barclays 'House of Fun' tour note (eve)": "2025-09-22",
    "2026-09-14 GS conf: Stack 'Mall developers love HoS'": "2026-09-14",
}
rows = []
for name, d in events.items():
    d = pd.Timestamp(d)
    i = r.index.searchsorted(d)
    win1 = r.iloc[i]
    win3 = (1 + r.iloc[i:i + 3]).prod() - 1
    rows.append(dict(event=name, date=r.index[i].date(), dks_1d=round(win1.DKS * 100, 2),
                     abn_vs_xrt_1d=round((win1.DKS - win1.XRT) * 100, 2), abn_vs_aso_1d=round((win1.DKS - win1.ASO) * 100, 2),
                     dks_3d=round(win3.DKS * 100, 2), abn_vs_xrt_3d=round((win3.DKS - win3.XRT) * 100, 2)))
df = pd.DataFrame(rows); print(df.to_string(index=False))
df.to_csv(os.path.join(os.path.dirname(__file__), "..", "raw", "F4_hos_event_returns.csv"), index=False)
