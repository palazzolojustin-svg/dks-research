"""P3: DKS average ticket vs official category prices (CPI), FY2016-Q2 FY2026, and a 3Q26-2Q27 ticket projection vs consensus.
Rerun: python THESIS_SCRAPE\\scripts\\P3_ticket_model.py   (needs raw\\P3_bls_levels.csv from P3_bls_prices.py and raw\\P3_bls_raw_cpi_2007_2016.json)
Inputs:
  - DKS sales-per-transaction ("ticket") and transactions by quarter: 10-Q/10-K MD&A (raw\\P3_edgar_ticket_sentences.txt for FY16-FY23Q1;
    WORKING_NOTES W03/W04 and earnings calls for FY23-FY26). Q4 values marked 'd' are derived from FY minus 39-week figures (weights ~0.69/0.31).
  - BLS CPI-U NSA US city average: SERC sporting goods, SEAE footwear, SAA apparel; SA versions for momentum.
DKS fiscal quarters: Q1 Feb-Apr, Q2 May-Jul, Q3 Aug-Oct, Q4 Nov-Jan (FY2026 = Feb-2026..Jan-2027).
Outputs: raw\\P3_ticket_vs_cpi_quarterly.csv, raw\\P3_ticket_projection.csv
"""
import json
import numpy as np, pandas as pd

RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw"
W = {"CPI Footwear": 0.289, "CPI Apparel": 0.340, "CPI Sporting goods": 0.371}  # DICK'S FY24 mix 28/33/36 (ex other 3%), renormalised

# (FY, Q): (ticket %, transactions %, comp %, source flag) ; consolidated DKS pre-FL (FY17-FY23 "consolidated" = DKS Inc; GG/FS included)
TICKET = {
    (2016, 1): (1.0, -0.5), (2016, 2): (1.3, 1.7), (2016, 3): (1.3, 4.2), (2016, 4): (2.5, 2.8),   # Q4 d from FY16 1.6/2.1 and 39w 1.2/1.8 (DSG banner)
    (2017, 1): (1.6, 0.8), (2017, 2): (2.1, -2.0), (2017, 3): (0.0, -0.9), (2017, 4): (-2.0, 0.0),  # Q4 d from FY17 0.2/-0.5, 39w 1.2/-0.7
    (2018, 1): (1.2, -3.7), (2018, 2): (0.7, -4.7), (2018, 3): (1.6, -5.5), (2018, 4): (1.4, -3.6),  # Q4 d from FY18 1.2/-4.3, 39w 1.1/-4.6
    (2019, 1): (1.0, -1.0), (2019, 2): (2.1, 1.1), (2019, 3): (2.7, 3.3), (2019, 4): (2.2, 2.8),     # Q4 d from FY19 2.0/1.7, 39w 1.9/1.2
    (2020, 1): (9.2, -38.7), (2020, 2): (17.9, 2.8), (2020, 3): (19.6, 3.6),                          # COVID: excluded from fit
    (2021, 2): (7.1, 12.1), (2021, 3): (3.7, 8.5),                                                   # stimulus/COVID lap: excluded
    (2022, 1): (-2.0, -6.4), (2022, 2): (3.3, -8.4), (2022, 3): (2.8, 3.7), (2022, 4): (-1.8, 6.0),  # Q4 d from FY22 0.2/-0.7, 39w 1.1/-3.7 (approx)
    (2023, 1): (0.7, 2.7), (2023, 2): (-1.0, 2.8), (2023, 3): (0.6, 1.1), (2023, 4): (2.7, 0.0),     # Q4 d from FY23 0.8/1.6, 39w 0.0/2.3
    (2024, 1): (2.6, 2.7), (2024, 2): (3.5, 1.0), (2024, 3): (4.8, -0.6), (2024, 4): (4.7, 1.7),     # Q4 d from FY24 4.0/1.2, 39w 3.7/1.0
    (2025, 1): (3.7, 0.8), (2025, 2): (4.1, 0.9), (2025, 3): (4.4, 1.3), (2025, 4): (4.4, -1.3),
    (2026, 1): (5.5, 0.5), (2026, 2): (3.6, 1.3),
}
CONS = {(2026, 3): (1.25, 1.50, 1.69), (2026, 4): (1.00, 1.57, 1.59), (2027, 1): (1.00, 1.00, 2.41), (2027, 2): (1.00, 1.00, 2.24)}
# consensus DICK'S segment revenue by quarter ($M): Q3 from BBG DICK'S OI 246.4 / 7.17%; Q4 = 2H 7,581 - Q3; FY27 Q1/Q2 = FY26A x (15,203/14,753) INFERENCE
REV = {(2026, 3): 3437.0, (2026, 4): 4144.0, (2027, 1): 3377.4 * 15203 / 14753, (2027, 2): 3849.9 * 15203 / 14753}
EPS_PER_M = 0.00814  # $/share per $1M pre-tax (89.09M sh, 27.46% tax)


def fq(period):
    y, m = period.year, period.month
    if m == 1:
        return (y - 1, 4)
    fy = y
    q = {2: 1, 3: 1, 4: 1, 5: 2, 6: 2, 7: 2, 8: 3, 9: 3, 10: 3, 11: 4, 12: 4}[m]
    return (fy, q)


def load_levels():
    lv = pd.read_csv(f"{RAW}\\P3_bls_levels.csv", index_col=0)
    js = json.load(open(f"{RAW}\\P3_bls_raw_cpi_2007_2016.json"))
    names = {"CUUR0000SERC": "CPI Sporting goods", "CUUR0000SEAE": "CPI Footwear", "CUUR0000SAA": "CPI Apparel", "CUUR0000SA0": "CPI All items",
             "CUUR0000SERC02": "CPI Sports equipment", "CUUR0000SACL1": "CPI Commodities less food energy"}
    rows = []
    for s in js["Results"]["series"]:
        for d in s["data"]:
            if d["period"].startswith("M") and d["period"] != "M13":
                rows.append({"name": names[s["seriesID"]], "date": f"{d['year']}-{d['period'][1:]}", "value": float(d["value"])})
    old = pd.DataFrame(rows).pivot_table(index="date", columns="name", values="value")
    lv = lv.combine_first(old)
    idx = pd.period_range("2007-01", lv.index.max(), freq="M")
    lv.index = pd.PeriodIndex(lv.index, freq="M")
    lv = lv.reindex(idx).interpolate(limit_area="inside", limit=1)  # fills Oct-2025 (not published) linearly; flagged
    return lv


def quarterly(lv, cols):
    q = lv[cols].copy()
    q["fq"] = [fq(p) for p in q.index]
    qa = q.groupby("fq").mean()
    n = q.groupby("fq").size()
    qa = qa[n == 3]
    yoy = qa.pct_change(4) * 100  # consecutive complete quarters from 2007 on
    return yoy


def main():
    lv = load_levels()
    cols = ["CPI Footwear", "CPI Apparel", "CPI Sporting goods", "CPI All items", "CPI Sports equipment"]
    yq = quarterly(lv, cols)
    yq["basket"] = sum(yq[c] * w for c, w in W.items())
    t = pd.DataFrame({k: {"ticket": v[0], "txn": v[1]} for k, v in TICKET.items()}).T
    lab = lambda k: f"Q{k[1]} FY{k[0] % 100:02d}"
    t.index = [lab(k) for k in t.index]
    yq.index = [lab(k) for k in yq.index]
    df = yq.join(t, how="left")
    df["spread"] = df["ticket"] - df["basket"]
    df = df.loc["Q1 FY15":]
    df.round(2).to_csv(f"{RAW}\\P3_ticket_vs_cpi_quarterly.csv")
    print(df.loc["Q1 FY16":, ["CPI Footwear", "CPI Apparel", "CPI Sporting goods", "basket", "ticket", "txn", "spread"]].round(1).to_string())

    fit = df.dropna(subset=["ticket", "basket"])
    fit = fit[~fit.index.str.contains("FY20|FY21")]
    X = np.c_[np.ones(len(fit)), fit["basket"].values]
    b, res, *_ = np.linalg.lstsq(X, fit["ticket"].values, rcond=None)
    pred = X @ b
    ss = ((fit["ticket"] - fit["ticket"].mean()) ** 2).sum()
    r2 = 1 - ((fit["ticket"] - pred) ** 2).sum() / ss
    resid_sd = np.std(fit["ticket"].values - pred, ddof=2)
    print(f"\nOLS ticket = {b[0]:.2f} + {b[1]:.2f} x basket ; R2 {r2:.2f}; n={len(fit)}; resid sd {resid_sd:.2f}")
    # pre-2024 vs 2024+ regimes
    for lab, sub in (("FY16-FY19", fit[fit.index.str.contains("FY1[6-9]")]), ("FY22-FY23", fit[fit.index.str.contains("FY2[23]")]),
                     ("FY24-FY26", fit[fit.index.str.contains("FY2[4-6]")])):
        print(lab, "mean ticket %.2f mean basket %.2f mean spread %.2f" % (sub.ticket.mean(), sub.basket.mean(), sub.spread.mean()))

    # ---- projection: CPI momentum scenarios from the Aug-2026 level
    sa = {"CPI Footwear": "CPI SA Footwear", "CPI Apparel": "CPI SA Apparel", "CPI Sporting goods": "CPI Sporting goods"}
    proj_idx = pd.period_range("2026-09", "2027-07", freq="M")
    out = []
    for scen, mom in (("zero momentum (SA level flat at Aug-26)", 0.0), ("trailing 6m SA momentum (Mar-Aug 26)", None), ("half of trailing 6m", 0.5)):
        lvp = {}
        for c, s in sa.items():
            ser = lv[s].dropna()
            ser = lv[s].interpolate(limit_area="inside")
            last = ser.loc[pd.Period("2026-08", "M")]
            if mom == 0.0:
                g = 0.0
            else:
                g6 = (ser.loc[pd.Period("2026-08", "M")] / ser.loc[pd.Period("2026-02", "M")]) ** (1 / 6) - 1
                g = g6 if mom is None else g6 * mom
            path = pd.Series([last * (1 + g) ** (i + 1) for i in range(len(proj_idx))], index=proj_idx)
            full = pd.concat([ser.loc[:pd.Period("2026-08", "M")], path])
            # y/y on SA levels (approximates NSA y/y); quarterly averages
            q = full.to_frame("v")
            q["fq"] = [fq(p) for p in q.index]
            qa = q.groupby("fq")["v"].mean()
            lvp[c] = qa.pct_change(4) * 100
        P = pd.DataFrame(lvp)
        P["basket"] = sum(P[c] * w for c, w in W.items())
        for k in [(2026, 3), (2026, 4), (2027, 1), (2027, 2)]:
            bk = P.loc[[k], "basket"].iloc[0]
            row = {"scenario": scen, "quarter": f"Q{k[1]} FY{k[0] % 100}", "footwear": P.loc[[k], "CPI Footwear"].iloc[0],
                   "apparel": P.loc[[k], "CPI Apparel"].iloc[0], "sporting": P.loc[[k], "CPI Sporting goods"].iloc[0], "basket": bk,
                   "ticket_ols": b[0] + b[1] * bk, "cons_ticket": CONS[k][0], "cons_txn": CONS[k][1], "cons_comp": CONS[k][2], "cons_rev": REV[k]}
            out.append(row)
    pr = pd.DataFrame(out)
    pr["ticket_gap_ols"] = pr["ticket_ols"] - pr["cons_ticket"]
    pr["rev_$M_ols"] = pr["ticket_gap_ols"] / 100 * pr["cons_rev"]
    for fl in (0.20, 0.25, 0.30):
        pr[f"eps_ols_fl{int(fl*100)}"] = pr["rev_$M_ols"] * fl * EPS_PER_M
    pr.round(3).to_csv(f"{RAW}\\P3_ticket_projection.csv", index=False)
    pd.set_option("display.width", 250)
    print(pr.round(2).to_string())


if __name__ == "__main__":
    main()
