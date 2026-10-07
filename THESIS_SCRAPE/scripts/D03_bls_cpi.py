"""D03: BLS CPI-U (NSA, US city avg) for DKS-relevant categories, 2023-2026, y/y %.
Rerun: python THESIS_SCRAPE\\scripts\\D03_bls_cpi.py   (BLS public API v1, no key; ~25 calls/day limit)
Output: THESIS_SCRAPE\\raw\\D03_bls_cpi.csv
"""
import json, requests, pandas as pd

SERIES = {
    "CUUR0000SERC": "Sporting goods",
    "CUUR0000SERC02": "Sports equipment",
    "CUUR0000SERC01": "Sports vehicles incl bicycles",
    "CUUR0000SEAE": "Footwear",
    "CUUR0000SEAE01": "Mens footwear",
    "CUUR0000SEAE02": "Boys and girls footwear",
    "CUUR0000SEAE03": "Womens footwear",
    "CUUR0000SAA": "Apparel",
    "CUUR0000SA0": "All items",
    "CUUR0000SEAA": "Mens and boys apparel",
}
OUT = r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\D03_bls_cpi.csv"


def main():
    rows = []
    ids = list(SERIES)
    payload = {"seriesid": ids, "startyear": "2023", "endyear": "2026"}
    r = requests.post("https://api.bls.gov/publicAPI/v1/timeseries/data/", json=payload, timeout=60)
    js = r.json()
    print(js.get("status"), js.get("message"))
    for s in js["Results"]["series"]:
        for d in s["data"]:
            if d["period"].startswith("M") and d["period"] != "M13" and d["value"] not in ("-", ""):
                rows.append({"series": s["seriesID"], "name": SERIES[s["seriesID"]], "date": f"{d['year']}-{d['period'][1:]}", "value": float(d["value"])})
    df = pd.DataFrame(rows).pivot_table(index="date", columns="name", values="value").sort_index()
    yoy = (df / df.shift(12) - 1) * 100
    out = df.join(yoy.add_suffix(" yoy%"))
    out.to_csv(OUT)
    print(yoy.loc["2025-01":].round(1).to_string())


if __name__ == "__main__":
    main()

