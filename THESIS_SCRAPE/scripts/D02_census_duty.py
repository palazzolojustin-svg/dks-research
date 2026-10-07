"""D02: effective US import duty rate by month for DKS-relevant HS chapters, from the Census International Trade API
(no key needed for light use). Effective rate = calculated duty (CAL_DUT_MO) / imports for consumption value (CON_VAL_MO).
Chapters: 61 knit apparel, 62 woven apparel, 64 footwear, 9506 sporting goods equipment, 4202 bags.
Rerun: python THESIS_SCRAPE\\scripts\\D02_census_duty.py   -> raw\\D02_census_duty.csv
"""
import requests, pandas as pd, time
BASE = "https://api.census.gov/data/timeseries/intltrade/imports/hs"
rows = []
months = [f"{y}-{m:02d}" for y in (2024, 2025, 2026) for m in range(1, 13)]
for comm, lvl in [("61", "HS2"), ("62", "HS2"), ("64", "HS2"), ("9506", "HS4"), ("4202", "HS4")]:
    for t in months:
        params = {"get": "CON_VAL_MO,CAL_DUT_MO,DUT_VAL_MO", "COMM_LVL": lvl, "I_COMMODITY": comm, "time": t}
        try:
            r = requests.get(BASE, params=params, timeout=40)
            if r.status_code != 200 or not r.text.startswith("["):
                continue
            j = r.json()
            hdr, vals = j[0], j[1]
            d = dict(zip(hdr, vals))
            con, dut = float(d["CON_VAL_MO"]), float(d["CAL_DUT_MO"])
            rows.append(dict(hs=comm, month=t, con_val=con, cal_duty=dut, eff_rate=dut / con if con else None))
        except Exception as e:
            print(comm, t, "ERR", str(e)[:80])
        time.sleep(0.2)
df = pd.DataFrame(rows)
df.to_csv(r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\D02_census_duty.csv", index=False)
pv = df.pivot(index="month", columns="hs", values="eff_rate").round(4)
print(pv.to_string())
