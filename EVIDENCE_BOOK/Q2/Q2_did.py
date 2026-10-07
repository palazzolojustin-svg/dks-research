"""Q2 task 1: difference-in-differences, DKS owned-brand share of apparel reviews vs Academy (ASO) private-label share.

Inputs (read-only, from PB_SCRAPE\\raw):
  R1_share_basket_month.csv  DKS basket x month, owned/total by variant (ALL, PIE, ORG, NONPIE)  [R1, pulled 2026-10-07 05:00-06:00 CDT]
  A1_aso_monthly.csv         ASO basket x month, owned/total by variant (ALLX, EMAIL, TEXT, PURCH, ORG)  [A1, pulled 2026-10-07 ~07:45 CDT]
Same method both sides: native (non-syndicated) reviews on apparel products (men's/women's/boys'/girls' apparel category trees),
owned share = owned-brand reviews / all-brand reviews in the same basket and months; pooled windows; binomial SEs.
Pairings:
  BROAD    DKS PIE+ORG (ex sampling/misc)   vs ASO ALLX (ex sampling)
  PROMPTED DKS PIE (post-purchase email)    vs ASO EMAIL (post-purchase email, unchanged program 2023-26) and ASO PURCH (email+SMS)
  ORGANIC  DKS ORG                           vs ASO ORG
Outputs: Q2_did_windows.csv (levels), Q2_did_table.csv (DiD), Q2_did_monthly.csv (monthly y/y DiD), printed tables.
RERUN: python Q2_did.py
"""
import os, math
import numpy as np, pandas as pd

RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\PB_SCRAPE\raw"
OUT = os.path.dirname(os.path.abspath(__file__))
WIN = {"Apr-Aug": [4, 5, 6, 7, 8], "Feb-Jul": [2, 3, 4, 5, 6, 7], "Q1 Feb-Apr": [2, 3, 4], "Q2 May-Jul": [5, 6, 7],
       "Aug": [8], "Sep": [9]}
BASK = ["APPAREL", "MENS", "WOMENS", "KIDS"]

# ---------- DKS monthly ----------
d = pd.read_csv(os.path.join(RAW, "R1_share_basket_month.csv"))
d = d[d.basket.isin(BASK)].copy()
dk = []
for _, r in d.iterrows():
    for v, (o, t) in {"PIE+ORG": (r.owned_PIE + r.owned_ORG, r.total_PIE + r.total_ORG), "PIE": (r.owned_PIE, r.total_PIE),
                      "ORG": (r.owned_ORG, r.total_ORG), "ALL": (r.owned_ALL, r.total_ALL)}.items():
        dk.append(("DKS", r.basket, r.month, v, o, t))
# ---------- ASO monthly ----------
a = pd.read_csv(os.path.join(RAW, "A1_aso_monthly.csv"))
a = a[a.basket.isin(BASK)]
ak = [("ASO", r.basket, r.month, r.variant, r.owned, r.total) for _, r in a.iterrows()]
m = pd.DataFrame(dk + ak, columns=["co", "basket", "month", "variant", "owned", "total"]).fillna(0)
m["y"] = m.month.str[:4].astype(int); m["mo"] = m.month.str[5:7].astype(int)

rows = []
for (co, b, v), g in m.groupby(["co", "basket", "variant"]):
    for wn, ms in WIN.items():
        for y in (2023, 2024, 2025, 2026):
            s = g[(g.y == y) & g.mo.isin(ms)]
            o, t = s.owned.sum(), s.total.sum()
            if t < 30:
                continue
            p = o / t
            ok = s[s.total >= 30]
            rows.append((co, b, v, wn, y, int(o), int(t), p, math.sqrt(p * (1 - p) / t), (ok.owned / ok.total).mean()))
W = pd.DataFrame(rows, columns=["co", "basket", "variant", "window", "year", "owned", "total", "share", "se", "eqw_month"])
W.to_csv(os.path.join(OUT, "Q2_did_windows.csv"), index=False)

PAIRS = {"BROAD (DKS PIE+ORG vs ASO ALLX)": ("PIE+ORG", "ALLX"), "PROMPTED (DKS PIE vs ASO EMAIL)": ("PIE", "EMAIL"),
         "PROMPTED2 (DKS PIE vs ASO EMAIL+SMS)": ("PIE", "PURCH"), "ORGANIC (DKS ORG vs ASO ORG)": ("ORG", "ORG"),
         "ALL (DKS ALL vs ASO ALLX)": ("ALL", "ALLX")}
lo = lambda p: math.log(p / (1 - p))
out = []
for pn, (dv, av) in PAIRS.items():
    for b in BASK:
        for wn in WIN:
            for y0, y1 in ((2024, 2025), (2025, 2026), (2024, 2026), (2023, 2024)):
                try:
                    D0, D1 = [W[(W.co == "DKS") & (W.basket == b) & (W.variant == dv) & (W.window == wn) & (W.year == y)].iloc[0] for y in (y0, y1)]
                    A0, A1 = [W[(W.co == "ASO") & (W.basket == b) & (W.variant == av) & (W.window == wn) & (W.year == y)].iloc[0] for y in (y0, y1)]
                except IndexError:
                    continue
                dd, da = D1.share - D0.share, A1.share - A0.share
                se = math.sqrt(D0.se ** 2 + D1.se ** 2 + A0.se ** 2 + A1.se ** 2)
                ddl = (lo(D1.share) - lo(D0.share)) - (lo(A1.share) - lo(A0.share))
                ew = (D1.eqw_month - D0.eqw_month) - (A1.eqw_month - A0.eqw_month)
                out.append((pn, b, wn, f"{y0}->{y1}", D0.share * 100, D1.share * 100, dd * 100, A0.share * 100, A1.share * 100, da * 100,
                            (dd - da) * 100, se * 100, (dd - da) / se, ddl, ew * 100, int(D1.total), int(A1.total)))
T = pd.DataFrame(out, columns=["pair", "basket", "window", "years", "dks_y0", "dks_y1", "dks_chg_pp", "aso_y0", "aso_y1", "aso_chg_pp",
                               "did_pp", "did_se_pp", "z", "did_logodds", "did_eqw_month_pp", "dks_n_y1", "aso_n_y1"])
T.to_csv(os.path.join(OUT, "Q2_did_table.csv"), index=False)

# ---------- monthly y/y DiD (apparel) ----------
mm = []
for dv, av, nm in (("PIE+ORG", "ALLX", "BROAD"), ("PIE", "EMAIL", "PROMPTED"), ("ORG", "ORG", "ORGANIC")):
    for y in (2025, 2026):
        for mo in range(1, 13):
            def sh(co, v, yy):
                s = m[(m.co == co) & (m.basket == "APPAREL") & (m.variant == v) & (m.y == yy) & (m.mo == mo)]
                return (s.owned.sum() / s.total.sum(), s.total.sum()) if s.total.sum() >= 30 else (np.nan, s.total.sum())
            d1, n1 = sh("DKS", dv, y); d0, _ = sh("DKS", dv, y - 1); a1, na = sh("ASO", av, y); a0, _ = sh("ASO", av, y - 1)
            mm.append((nm, f"{y}-{mo:02d}", d1 * 100, (d1 - d0) * 100, a1 * 100, (a1 - a0) * 100, ((d1 - d0) - (a1 - a0)) * 100, n1, na))
M = pd.DataFrame(mm, columns=["pair", "month", "dks_share", "dks_yoy_pp", "aso_share", "aso_yoy_pp", "did_pp", "dks_n", "aso_n"])
M.to_csv(os.path.join(OUT, "Q2_did_monthly.csv"), index=False)

if __name__ == "__main__":
    pd.set_option("display.width", 260); pd.set_option("display.max_rows", 500)
    print("=== LEVELS apparel, Apr-Aug and Feb-Jul (share %, n)")
    L = W[(W.basket == "APPAREL") & W.window.isin(["Apr-Aug", "Feb-Jul", "Aug", "Sep"])]
    L = L.assign(s=(L.share * 100).round(1).astype(str) + " (" + L.total.astype(str) + ")")
    print(L.pivot_table(index=["window", "co", "variant"], columns="year", values="s", aggfunc="first").to_string())
    print("\n=== DiD (pp); apparel + sub-baskets, Apr-Aug / Feb-Jul")
    x = T[T.window.isin(["Apr-Aug", "Feb-Jul"]) & T.years.isin(["2024->2025", "2025->2026", "2024->2026"])]
    print(x.round(2).to_string(index=False))
    print("\n=== monthly y/y (apparel)")
    print(M[M.pair == "BROAD"].round(1).to_string(index=False))
