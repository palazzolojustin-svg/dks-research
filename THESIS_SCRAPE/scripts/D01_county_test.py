"""D01: county-level QCEW test. Do sporting-goods establishments (NAICS 459110) shrink faster
in counties with a DICK'S store / a House of Sport than elsewhere?
Inputs: THESIS_SCRAPE/raw/H02_store_pages.json (H02's scrape of stores.dickssportinggoods.com, 778 stores,
lat/lon + ld_name "DICK'S House of Sport"). County FIPS via FCC Census Block API (public).
QCEW county rows (agglvl 78, private own_code 5) from https://data.bls.gov/cew/data/api/{y}/{q}/industry/459110.csv
Output: raw/D01_store_county.csv, raw/D01_county_test.csv. Rerun: python D01_county_test.py
"""
import io
import json
import os
import time

import pandas as pd
import requests

RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw"
H = {"User-Agent": "Mozilla/5.0 research"}
stores = json.load(open(os.path.join(RAW, "H02_store_pages.json"), encoding="utf-8"))
cache_f = os.path.join(RAW, "D01_store_county.csv")
# ZIP -> county via Census 2020 ZCTA-county relationship file (largest land-area overlap wins)
rel_f = os.path.join(RAW, "D01_zcta_county_rel.txt")
if not os.path.exists(rel_f):
    u = "https://www2.census.gov/geo/docs/maps-data/data/rel2020/zcta520/tab20_zcta520_county20_natl.txt"
    open(rel_f, "wb").write(requests.get(u, headers=H, timeout=300).content)
rel = pd.read_csv(rel_f, sep="|", dtype=str)
rel["AREALAND_PART"] = rel["AREALAND_PART"].astype(float)
rel = rel.dropna(subset=["GEOID_ZCTA5_20"]).sort_values("AREALAND_PART", ascending=False)
z2c = rel.drop_duplicates("GEOID_ZCTA5_20").set_index("GEOID_ZCTA5_20")["GEOID_COUNTY_20"].to_dict()
rows = []
for s in stores:
    z = (s.get("postalcode") or "")[:5]
    rows.append(dict(storeno=s["storeno"], state=s["state"], city=s["city"], zip=z, fips=z2c.get(z),
                     hos=str("House of Sport" in (s.get("ld_name") or ""))))
sc = pd.DataFrame(rows)
print("stores", len(sc), "unmapped", sc.fips.isna().sum(), "HoS", (sc.hos == "True").sum())
sc.to_csv(cache_f, index=False)


def q(y, qq):
    for i in range(6):
        try:
            r = requests.get(f"https://data.bls.gov/cew/data/api/{y}/{qq}/industry/459110.csv", headers=H, timeout=120)
            d = pd.read_csv(io.StringIO(r.text), dtype={"area_fips": str})
            d = d[(d.agglvl_code == 78) & (d.own_code == 5) & ~d.area_fips.str.startswith("09")]  # CT dropped (planning regions)
            return d.set_index("area_fips")[["qtrly_estabs", "month3_emplvl", "disclosure_code"]]
        except Exception:
            time.sleep(3 + 3 * i)


a = q(2023, 1)
b = q(2026, 1)
m = a.join(b, lsuffix="_23", rsuffix="_26", how="outer").fillna({"qtrly_estabs_23": 0, "qtrly_estabs_26": 0})
cnt = sc.groupby("fips").agg(n_dks=("storeno", "count"), n_hos=("hos", lambda x: (x == "True").sum()))
m = m.join(cnt, how="left").fillna({"n_dks": 0, "n_hos": 0})
m["grp"] = "no DKS"
m.loc[m.n_dks > 0, "grp"] = "DKS, no HoS"
m.loc[m.n_hos > 0, "grp"] = "HoS county"
m.to_csv(os.path.join(RAW, "D01_county_test.csv"))
g = m.groupby("grp").agg(counties=("qtrly_estabs_23", "size"), est23=("qtrly_estabs_23", "sum"),
                         est26=("qtrly_estabs_26", "sum"))
g["chg"] = g.est26 - g.est23
g["pct"] = (g.est26 / g.est23 - 1) * 100
print(g)
# employment where disclosed in both years
e = m[(m.disclosure_code_23 != "N") & (m.disclosure_code_26 != "N")]
ge = e.groupby("grp").agg(counties=("month3_emplvl_23", "size"), emp23=("month3_emplvl_23", "sum"),
                          emp26=("month3_emplvl_26", "sum"))
ge["pct"] = (ge.emp26 / ge.emp23 - 1) * 100
print(ge)

