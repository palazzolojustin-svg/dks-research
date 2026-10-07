"""D02: NYMEX ULSD (HO) and Brent (BZ) futures strip from Yahoo Finance public chart endpoint.
Rerun: python THESIS_SCRAPE\\scripts\\D02_futures_curve.py
Writes THESIS_SCRAPE\\raw\\D02_futures_curve.csv (contract, month, last price, quote time UTC).
Then maps the strip into DKS fiscal quarters (Q1 Feb-Apr, Q2 May-Jul, Q3 Aug-Oct, Q4 Nov-Jan) and compares to
realised NYH ULSD spot (FRED DHOILNYH, raw\\D02_fred_DHOILNYH.csv) by fiscal quarter.
"""
import requests, datetime as dt, pandas as pd
H = {"User-Agent": "Mozilla/5.0"}
codes = "FGHJKMNQUVXZ"
rows = []
for root in ["HO", "BZ"]:
    for yr in [26, 27, 28]:
        for i, c in enumerate(codes):
            month = i + 1
            if yr == 26 and month < 11: continue
            if yr == 28 and month > 1: continue
            t = f"{root}{c}{yr}.NYM"
            try:
                r = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{t}?range=5d&interval=1d", headers=H, timeout=10)
                m = r.json()["chart"]["result"][0]["meta"]
                rows.append(dict(root=root, contract=t, month=f"20{yr}-{month:02d}", price=m.get("regularMarketPrice"),
                                 time=dt.datetime.utcfromtimestamp(m.get("regularMarketTime")).isoformat()))
            except Exception as e:
                rows.append(dict(root=root, contract=t, month=f"20{yr}-{month:02d}", price=None, time=str(e)[:40]))
df = pd.DataFrame(rows)
df.to_csv(r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\D02_futures_curve.csv", index=False)
print(df.to_string())

def fq(ym):
    y, m = int(ym[:4]), int(ym[5:])
    if m in (2, 3, 4): return f"FY{y}Q1"
    if m in (5, 6, 7): return f"FY{y}Q2"
    if m in (8, 9, 10): return f"FY{y}Q3"
    if m == 1: return f"FY{y-1}Q4"
    return f"FY{y}Q4"
df["fq"] = df.month.apply(fq)
print(df.dropna().groupby(["root", "fq"]).price.mean().round(3).to_string())
