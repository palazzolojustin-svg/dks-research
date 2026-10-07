"""P3: BLS official price data for DKS categories: CPI detail, import price indexes (MXP), PPI (manufacturing + retail/wholesale margin PPIs).
Rerun: python THESIS_SCRAPE\\scripts\\P3_bls_prices.py   (BLS public API v1, no key; 25 queries/day/IP; 25 series & 10 yrs per query)
Series IDs for MXP taken from BLS series_identifiers.xlsx (saved raw\\P3_mxp_series_identifiers.xlsx).
Outputs: raw\\P3_bls_levels.csv (monthly levels, wide), raw\\P3_bls_yoy.csv (y/y %), raw\\P3_bls_raw_<grp>.json
"""
import json, sys, requests, pandas as pd

RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw"
CPI = {
    "CUUR0000SERC": "CPI Sporting goods", "CUUR0000SERC01": "CPI Sports vehicles incl bicycles", "CUUR0000SERC02": "CPI Sports equipment",
    "CUUR0000SEAE": "CPI Footwear", "CUUR0000SEAE01": "CPI Mens footwear", "CUUR0000SEAE02": "CPI Boys girls footwear", "CUUR0000SEAE03": "CPI Womens footwear",
    "CUUR0000SAA": "CPI Apparel", "CUUR0000SAA1": "CPI Mens boys apparel", "CUUR0000SAA2": "CPI Womens girls apparel",
    "CUUR0000SEAA": "CPI Mens apparel", "CUUR0000SEAB": "CPI Boys apparel", "CUUR0000SEAC": "CPI Womens apparel", "CUUR0000SEAD": "CPI Girls apparel",
    "CUUR0000SA0": "CPI All items", "CUUR0000SA0L1E": "CPI Core", "CUUR0000SACL1": "CPI Commodities less food energy",
    "CUSR0000SERC": "CPI SA Sporting goods", "CUSR0000SEAE": "CPI SA Footwear", "CUSR0000SAA": "CPI SA Apparel", "CUSR0000SERC02": "CPI SA Sports equipment",
    "CUSR0000SACL1": "CPI SA Core goods",
}
MXP = {
    "EIUIR4": "MXP Consumer goods ex auto", "EIUIR400": "MXP Apparel footwear household", "EIUIR40000": "MXP Cotton apparel household",
    "EIUIR40020": "MXP Apparel other textiles", "EIUIR40030": "MXP Nontextile apparel household", "EIUIR40040": "MXP Footwear (end use)",
    "EIUIR40050": "MXP Sporting camping apparel footwear", "EIUIR411": "MXP Recreational equipment", "EIUIR41120": "MXP Toys shooting sporting goods",
    "EIUIP64": "MXP HS64 Footwear", "EIUIP6402": "MXP HS6402 rubber/plastic footwear", "EIUIP6404": "MXP HS6404 textile-upper footwear",
    "EIUIP61": "MXP HS61 knit apparel", "EIUIP62": "MXP HS62 woven apparel", "EIUIP95": "MXP HS95 toys games sports equip",
    "EIUIZ3162": "MXP NAICS footwear mfg", "EIUIZ33992": "MXP NAICS sporting athletic goods mfg", "EIUIZ315": "MXP NAICS apparel mfg",
    "EIUCOCHNZ3162": "MXP China footwear", "EIUCOCHNZ315": "MXP China apparel", "EIUCOPRIMZ3162": "MXP PacRim footwear",
    "EIUCOASEANZ315": "MXP ASEAN apparel", "EIUCOCHNZ3399": "MXP China other misc mfg", "EIUCOCHNTOT": "MXP China all", "EIUCOASEANTOT": "MXP ASEAN all",
}
PPI = {
    "PCU316210316210": "PPI Footwear mfg", "PCU339920339920": "PPI Sporting athletic goods mfg",
    "PCU459110459110": "PPI Sporting goods retailers (margin)", "PCU458210458210": "PPI Shoe retailers (margin)",
    "PCU458110458110": "PPI Clothing retailers (margin)", "PCU423910423910": "PPI Sporting goods wholesalers (margin)",
    "PCU424340424340": "PPI Footwear wholesalers (margin)", "PCU451110451110": "PPI Sporting goods stores old code",
    "PCU315315": "PPI Apparel mfg", "PCU33992033992014": "PPI athletic goods sub (test)",
}
GROUPS = {"cpi": CPI, "mxp": MXP, "ppi": PPI}


def fetch(grp, ids, start="2017", end="2026"):
    r = requests.post("https://api.bls.gov/publicAPI/v1/timeseries/data/",
                      json={"seriesid": list(ids), "startyear": start, "endyear": end}, timeout=120)
    js = r.json()
    json.dump(js, open(f"{RAW}\\P3_bls_raw_{grp}.json", "w"))
    print(grp, js.get("status"), js.get("message"))
    return js


def parse(js, names):
    rows = []
    for s in js["Results"]["series"]:
        for d in s["data"]:
            if d["period"].startswith("M") and d["period"] != "M13" and d["value"] not in ("-", ""):
                try:
                    v = float(d["value"])
                except ValueError:
                    continue
                rows.append({"name": names[s["seriesID"]], "date": f"{d['year']}-{d['period'][1:]}", "value": v})
    return rows


def main(groups):
    rows = []
    for g in groups:
        js = fetch(g, GROUPS[g])
        rows += parse(js, GROUPS[g])
    df = pd.DataFrame(rows).pivot_table(index="date", columns="name", values="value").sort_index()
    try:
        old = pd.read_csv(f"{RAW}\\P3_bls_levels.csv", index_col=0)
        df = old.combine_first(df) if False else df.combine_first(old)
    except FileNotFoundError:
        pass
    full = pd.period_range(df.index.min(), df.index.max(), freq="M").strftime("%Y-%m")
    df = df.reindex(full)  # keeps gaps (e.g. Oct-2025 CPI not published) as NaN so shift(12) is calendar-correct
    df.to_csv(f"{RAW}\\P3_bls_levels.csv")
    yoy = (df / df.shift(12) - 1) * 100
    yoy.to_csv(f"{RAW}\\P3_bls_yoy.csv")
    print(df.tail(3).T.to_string())


if __name__ == "__main__":
    main(sys.argv[1:] or ["cpi", "mxp", "ppi"])
