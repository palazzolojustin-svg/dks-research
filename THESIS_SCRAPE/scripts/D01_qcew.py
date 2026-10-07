"""D01: BLS QCEW national series for sporting-goods, shoe and department-store retailers.
Pulls https://data.bls.gov/cew/data/api/{year}/{qtr}/industry/{naics}.csv (public open-data API),
keeps US total (area_fips US000), private ownership (own_code 5), and writes
THESIS_SCRAPE/raw/D01_qcew_national.csv (+ state-level for sporting goods to D01_qcew_states_sg.csv).
NAICS 2022 codes from 2022Q1 onward (459110 sporting goods, 458210 shoe, 455110 dept stores);
NAICS 2017 codes before (451110, 448210, 452210 [dept stores 2017 = 452210]).
Rerun: python D01_qcew.py
"""
import io
import time

import pandas as pd
import requests

H = {"User-Agent": "Mozilla/5.0 research"}
SERIES = {
    "sporting_goods": ("451110", "459110"),
    "shoe": ("448210", "458210"),
    "dept_store": ("452210", "455110"),
}
OUT = r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw"


def get(year, q, code):
    u = f"https://data.bls.gov/cew/data/api/{year}/{q}/industry/{code}.csv"
    for i in range(6):
        try:
            r = requests.get(u, headers=H, timeout=90)
        except Exception as e:  # SSL EOF etc: back off and retry
            print("retry", u, e.__class__.__name__)
            time.sleep(3 + 3 * i)
            continue
        if r.status_code == 200:
            return pd.read_csv(io.StringIO(r.text), dtype={"area_fips": str})
        if r.status_code == 404:
            return None
        time.sleep(3 + 3 * i)
    return None


rows, states = [], []
for name, (old, new) in SERIES.items():
    for y in range(2018, 2027):
        for q in range(1, 5):
            code = new if y >= 2022 else old
            df = get(y, q, code)
            if df is None:
                continue
            us = df[(df.area_fips == "US000") & (df.own_code == 5)]
            if len(us):
                r0 = us.iloc[0]
                rows.append(dict(series=name, naics=code, year=y, qtr=q, estabs=r0.qtrly_estabs,
                                 emp_m3=r0.month3_emplvl, wages=r0.total_qtrly_wages,
                                 oty_estabs_pct=r0.oty_qtrly_estabs_pct_chg,
                                 oty_emp3_pct=r0.oty_month3_emplvl_pct_chg))
            if name == "sporting_goods":
                st = df[(df.own_code == 5) & (df.agglvl_code == 56)]  # state, by NAICS 6-digit
                for _, s in st.iterrows():
                    states.append(dict(area_fips=s.area_fips, year=y, qtr=q, estabs=s.qtrly_estabs,
                                       emp_m3=s.month3_emplvl, disclosure=s.disclosure_code))
            print(name, y, q, "ok")

pd.DataFrame(rows).to_csv(OUT + r"\D01_qcew_national.csv", index=False)
pd.DataFrame(states).to_csv(OUT + r"\D01_qcew_states_sg.csv", index=False)
print("done")
