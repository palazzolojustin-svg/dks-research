"""D02: DKS (DICK'S segment) fuel-cost sensitivity by fiscal quarter, FY25A-FY27E.
Inputs: raw\\D02_fred_GASDESW.csv (EIA retail diesel weekly), raw\\D02_futures_curve.csv (NYMEX HO strip 2026-10-07).
FY27 retail diesel = HO futures + retail-minus-NYH spread (avg FY25Q1-FY26Q3 = computed below).
ASSUMPTIONS (INFERENCE, calibrate if better data appears):
  - fuel-exposed trucking spend (inbound + DC->store TL/LTL) = 1.5% of DICK'S sales; fuel = 27% of that at $3.65 diesel
  - parcel spend (ship-to-home) = 1.0% of DICK'S sales incl. fuel surcharge; surcharge % = FedEx Ground table approx
    (~20% at $3.65; +0.25pt per $0.09 above $4.99 -> 29.25% at $6.34-6.43) -> linearised: 20% + 3.6pt per $1 above $3.65
  - DICK'S quarterly sales: FY26E/FY27E from consensus seg revenue ($14,753M / $15,203M) split by FY25 seasonality.
Calibration check: FY22 10-K attributed ~35bps of a -369bps GM decline to eCom shipping (rates + penetration) when diesel rose ~50%.
Rerun: python THESIS_SCRAPE\\scripts\\D02_fuel_sensitivity.py
"""
import pandas as pd
RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw"
def fq(ts):
    m, y = ts.month, ts.year
    return f"FY{y}Q1" if m in (2,3,4) else f"FY{y}Q2" if m in (5,6,7) else f"FY{y}Q3" if m in (8,9,10) else (f"FY{y-1}Q4" if m == 1 else f"FY{y}Q4")
d = pd.read_csv(f"{RAW}\\D02_fred_GASDESW.csv", parse_dates=["date"])
d["fq"] = d.date.apply(fq)
retail = d.groupby("fq").v.mean()
ny = pd.read_csv(f"{RAW}\\D02_fred_DHOILNYH.csv", parse_dates=["date"]); ny["fq"] = ny.date.apply(fq)
nyq = ny.groupby("fq").v.mean()
qs = ["FY2025Q1","FY2025Q2","FY2025Q3","FY2025Q4","FY2026Q1","FY2026Q2","FY2026Q3"]
spread = (retail[qs] - nyq[qs]).mean()
fut = pd.read_csv(f"{RAW}\\D02_futures_curve.csv"); fut = fut[fut.root == "HO"].dropna(subset=["price"])
fut["fq"] = fut.month.apply(lambda s: fq(pd.Timestamp(s + "-15")))
futq = fut.groupby("fq").price.mean() + spread
path = {q: retail[q] for q in qs}
path["FY2025Q3"] = retail["FY2025Q3"]
for q in ["FY2026Q4","FY2027Q1","FY2027Q2","FY2027Q3","FY2027Q4"]:
    path[q] = futq[q]
# FY26Q3 is partial (to 2026-10-05); assume rest of October at last print
sales_fy25 = {"Q1":3174.7,"Q2":3646.6,"Q3":3236.9,"Q4":4050.8}  # $M DICK'S segment FY25 actual
tot25 = sum(sales_fy25.values())
def sales(q):
    fy = q[:6]; qq = q[-2:]
    base = {"FY2025":tot25, "FY2026":14753.0, "FY2027":15203.0}[fy]
    return base * sales_fy25[qq] / tot25
def fuel_cost(q):
    p = path[q]; s = sales(q)
    truck = s*0.015*(1 - 0.27 + 0.27*p/3.65)
    surch = 0.20 + 0.036*(p-3.65)
    parcel = s*0.010/1.20*(1+surch)
    return truck + parcel
rows = []
for q in ["FY2026Q1","FY2026Q2","FY2026Q3","FY2026Q4","FY2027Q1","FY2027Q2","FY2027Q3","FY2027Q4"]:
    py = q.replace("2026","2025") if "2026" in q else q.replace("2027","2026")
    c, cp = fuel_cost(q), fuel_cost(py) * sales(q)/sales(py)
    rows.append(dict(q=q, diesel=round(path[q],2), diesel_py=round(path[py],2), yoy=f"{path[q]/path[py]-1:+.0%}",
                     cost_delta_M=round(c-cp,1), bps_of_sales=round((c-cp)/sales(q)*1e4,1)))
out = pd.DataFrame(rows)
print(f"retail-minus-NYH spread used: {spread:.3f}")
print(out.to_string(index=False))
for fy in ["FY2026","FY2027"]:
    sub = out[out.q.str.startswith(fy)]
    tot = sum(sales(q) for q in sub.q)
    print(fy, "fuel cost delta $M", round(sub.cost_delta_M.sum(),1), "bps", round(sub.cost_delta_M.sum()/tot*1e4,1))
out.to_csv(f"{RAW}\\D02_fuel_sensitivity.csv", index=False)
