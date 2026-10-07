"""D01: control test for the county result. Same county groups (DKS counties / HoS counties / no-DKS)
built by D01_county_test.py (raw/D01_store_county.csv), applied to other retail industries, so we can
tell a DKS-specific competitor exit from a general urban-retail decline.
Industries: 459110 sporting goods, 458210 shoe, 459120 hobby/toy/game, 445110 supermarkets, 44-45 all retail.
Q1-2023 vs Q1-2026 (March), US private, county level. Output raw/D01_county_control.csv.
Also writes distribution stats for 459110 (share of counties declining, medians) and the top-decline DKS counties.
Rerun: python D01_county_control.py
"""
import io
import time

import pandas as pd
import requests

RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw"
H = {"User-Agent": "Mozilla/5.0 research"}
sc = pd.read_csv(RAW + r"\D01_store_county.csv", dtype=str)
cnt = sc.dropna(subset=["fips"]).groupby("fips").agg(n_dks=("storeno", "count"),
                                                      n_hos=("hos", lambda x: (x == "True").sum()))


def q(y, qq, ind):
    for i in range(6):
        try:
            r = requests.get(f"https://data.bls.gov/cew/data/api/{y}/{qq}/industry/{ind}.csv", headers=H, timeout=180)
            d = pd.read_csv(io.StringIO(r.text), dtype={"area_fips": str})
            d = d[(d.own_code == 5) & d.area_fips.str.match(r"^\d{5}$") & ~d.area_fips.str.endswith("000") & ~d.area_fips.str.startswith("09")]  # CT dropped: counties->planning regions in 2024+
            d = d[d.agglvl_code == d.agglvl_code.max()] if ind != "44_45" else d[d.agglvl_code == 74]
            return d.set_index("area_fips")[["qtrly_estabs", "month3_emplvl", "disclosure_code"]]
        except Exception as e:
            print("retry", ind, y, e)
            time.sleep(3 + 3 * i)


out = []
for ind in ["459110", "458210", "459120", "445110", "44_45"]:
    a, b = q(2023, 1, ind), q(2026, 1, ind)
    m = a.join(b, lsuffix="_23", rsuffix="_26", how="outer").fillna({"qtrly_estabs_23": 0, "qtrly_estabs_26": 0})
    m = m.join(cnt, how="left").fillna({"n_dks": 0, "n_hos": 0})
    m["grp"] = "no DKS"
    m.loc[m.n_dks > 0, "grp"] = "DKS, no HoS"
    m.loc[m.n_hos > 0, "grp"] = "HoS county"
    for g, x in m.groupby("grp"):
        e = x[(x.disclosure_code_23 != "N") & (x.disclosure_code_26 != "N")]
        out.append(dict(industry=ind, grp=g, counties=len(x), est23=x.qtrly_estabs_23.sum(),
                        est26=x.qtrly_estabs_26.sum(),
                        est_pct=(x.qtrly_estabs_26.sum() / x.qtrly_estabs_23.sum() - 1) * 100,
                        emp_pct_disclosed=(e.month3_emplvl_26.sum() / e.month3_emplvl_23.sum() - 1) * 100))
    if ind == "459110":
        d = m[m.n_dks > 0].copy()
        d["chg"] = d.qtrly_estabs_26 - d.qtrly_estabs_23
        d["pct"] = d.chg / d.qtrly_estabs_23 * 100
        print("459110 DKS counties: share with fewer estabs", round((d.chg < 0).mean() * 100, 1),
              "share more", round((d.chg > 0).mean() * 100, 1), "median pct", round(d.pct.median(), 1))
        nd = m[m.n_dks == 0]
        nd = nd[nd.qtrly_estabs_23 > 0]
        print("459110 no-DKS counties: share fewer", round(((nd.qtrly_estabs_26 - nd.qtrly_estabs_23) < 0).mean() * 100, 1),
              "share more", round(((nd.qtrly_estabs_26 - nd.qtrly_estabs_23) > 0).mean() * 100, 1))
        big = d[d.qtrly_estabs_23 >= 40]
        print("DKS counties with >=40 estabs:", len(big), "pct chg", round((big.qtrly_estabs_26.sum() / big.qtrly_estabs_23.sum() - 1) * 100, 2))
        d.sort_values("chg").head(15).to_csv(RAW + r"\D01_county_top_declines.csv")
        print(d.sort_values("chg")[["qtrly_estabs_23", "qtrly_estabs_26", "chg", "n_dks", "n_hos"]].head(15))
    print(ind, "ok")
o = pd.DataFrame(out)
o.to_csv(RAW + r"\D01_county_control.csv", index=False)
pd.set_option("display.width", 200)
print(o.round(2).to_string(index=False))

