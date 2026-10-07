"""D01: BLS QCEW Q1 establishment-size-class data for sporting-goods retailers (US, private).
Source: https://data.bls.gov/cew/data/api/{year}/1/size/{size_code}.csv (size data exist for Q1 only).
NAICS 451110 (<=2021) / 459110 (>=2022). Size codes: 1:<5, 2:5-9, 3:10-19, 4:20-49, 5:50-99, 6:100-249,
7:250-499, 8:500-999, 9:1000+ employees (March employment).
Output: THESIS_SCRAPE/raw/D01_qcew_size_sg.csv. Rerun: python D01_qcew_size.py
"""
import io
import time

import pandas as pd
import requests

H = {"User-Agent": "Mozilla/5.0 research"}
rows = []
for y in range(2019, 2027):
    code = "459110" if y >= 2022 else "451110"
    for s in range(1, 10):
        u = f"https://data.bls.gov/cew/data/api/{y}/1/size/{s}.csv"
        d = None
        for i in range(6):
            try:
                r = requests.get(u, headers=H, timeout=200)
                if r.status_code == 200:
                    d = pd.read_csv(io.StringIO(r.text), dtype={"area_fips": str, "industry_code": str})
                    break
            except Exception as e:
                print("retry", u, e.__class__.__name__)
            time.sleep(3 + 3 * i)
        if d is None:
            print("FAIL", u)
            continue
        x = d[(d.industry_code == code) & (d.area_fips == "US000") & (d.own_code == 5)]
        for _, r0 in x.iterrows():
            rows.append(dict(year=y, size_code=s, naics=code, estabs=r0.qtrly_estabs, emp_m1=r0.month1_emplvl,
                             disclosure=r0.disclosure_code))
        print(y, s, len(x))
pd.DataFrame(rows).to_csv(r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\D01_qcew_size_sg.csv", index=False)
print("done")
