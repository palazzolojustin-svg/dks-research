"""D02: pull cost-input series from FRED (no API key; fredgraph.csv endpoint).
Rerun: python THESIS_SCRAPE\\scripts\\D02_fred_costs.py
Writes THESIS_SCRAPE\\raw\\D02_fred_<id>.csv and prints y/y comparisons by DKS fiscal quarter.
DKS fiscal quarters (approx): Q1 Feb-Apr, Q2 May-Jul, Q3 Aug-Oct, Q4 Nov-Jan.
"""
import io, sys, requests, pandas as pd

SERIES = {
    "GASDESW": "US No2 diesel retail $/gal weekly (EIA via FRED)",
    "GASREGW": "US regular gasoline retail $/gal weekly",
    "DCOILBRENTEU": "Brent spot $/bbl daily",
    "DHOILNYH": "NY Harbor ULSD/heating oil spot $/gal daily",
    "PCU484121484121": "PPI general freight trucking long-distance TL",
    "PCU4841248412": "PPI general freight trucking long distance (LTL/TL)",
    "PCU492110492110": "PPI couriers and express delivery services",
    "PCU483111483111": "PPI deep sea freight transportation",
    "CES4200000003": "Avg hourly earnings retail trade all employees",
    "CES4245200003": "Avg hourly earnings general merchandise retailers (fallback)",
    "CPIMEDSL": "CPI medical care",
    "ECIWAG": "ECI wages private",
    "TSIFRGHT": "Transportation services index freight",
    "CASSHIPMENTS": "placeholder",
}
OUT = r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw"

def fiscal_q(ts):
    m, y = ts.month, ts.year
    if m in (2, 3, 4): return f"FY{y}Q1"
    if m in (5, 6, 7): return f"FY{y}Q2"
    if m in (8, 9, 10): return f"FY{y}Q3"
    if m == 1: return f"FY{y-1}Q4"
    return f"FY{y}Q4"

for sid, desc in SERIES.items():
    try:
        r = requests.get(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}", timeout=40)
        if r.status_code != 200 or "DATE" not in r.text[:50].upper():
            print(sid, "FAILED", r.status_code); continue
        df = pd.read_csv(io.StringIO(r.text))
        df.columns = ["date", "v"]
        df["date"] = pd.to_datetime(df["date"])
        df["v"] = pd.to_numeric(df["v"], errors="coerce")
        df = df.dropna()
        df.to_csv(f"{OUT}\\D02_fred_{sid}.csv", index=False)
        d = df[df.date >= "2024-02-01"].copy()
        d["fq"] = d.date.apply(fiscal_q)
        q = d.groupby("fq").v.mean()
        print(f"\n== {sid}: {desc} | last {df.date.iloc[-1].date()} = {df.v.iloc[-1]}")
        print(q.round(3).to_string())
    except Exception as e:
        print(sid, "ERR", e)
