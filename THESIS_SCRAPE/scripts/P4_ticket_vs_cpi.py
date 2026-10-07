"""P4: DKS same-store ticket vs CPI (sporting goods / footwear / apparel) by DKS fiscal quarter, FY2018-Q2 FY2026.
Inputs: raw/P4_ticket_history.csv (P4), raw/P3_bls_yoy.csv (P3 BLS pull, NSA y/y %).
DKS fiscal quarters: Q1 = Feb-Apr, Q2 = May-Jul, Q3 = Aug-Oct, Q4 = Nov-Jan (FYxx Q4 ends Jan of xx+1).
Basket = 0.45*footwear + 0.25*apparel + 0.30*sporting goods (INFERENCE weights; DKS mix ~ footwear/apparel/hardlines).
Rerun: python P4_ticket_vs_cpi.py -> raw/P4_ticket_vs_cpi.csv, prints spread stats.
"""
import csv, os, statistics as st
RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw"
cpi = {}
with open(os.path.join(RAW, "P3_bls_yoy.csv")) as fh:
    r = csv.DictReader(fh)
    for row in r:
        m = row[""]
        def g(k):
            v = row.get(k, "")
            return float(v) if v not in ("", None) else None
        cpi[m] = (g("CPI Sporting goods"), g("CPI Footwear"), g("CPI Apparel"))
tick = {}
with open(os.path.join(RAW, "P4_ticket_history.csv")) as fh:
    for row in csv.DictReader(fh):
        if row["type"] in ("reported", "derived") and row["period"].startswith("Q"):
            tick[row["period"]] = float(row["ticket_pct"])

def months(q, fy):
    y = 2000 + fy
    if q == 1: return [f"{y}-02", f"{y}-03", f"{y}-04"]
    if q == 2: return [f"{y}-05", f"{y}-06", f"{y}-07"]
    if q == 3: return [f"{y}-08", f"{y}-09", f"{y}-10"]
    return [f"{y}-11", f"{y}-12", f"{y+1}-01"]

out = []
for fy in range(18, 27):
    for q in (1, 2, 3, 4):
        p = f"Q{q}FY{fy}"
        if p not in tick: continue
        vals = [cpi.get(m) for m in months(q, fy)]
        vals = [v for v in vals if v and all(x is not None for x in v)]
        if not vals: continue
        sg = st.mean(v[0] for v in vals); fw = st.mean(v[1] for v in vals); ap = st.mean(v[2] for v in vals)
        basket = 0.45 * fw + 0.25 * ap + 0.30 * sg
        out.append([p, tick[p], round(sg, 2), round(fw, 2), round(ap, 2), round(basket, 2), round(tick[p] - basket, 2), len(vals)])
with open(os.path.join(RAW, "P4_ticket_vs_cpi.csv"), "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["period", "dks_ticket", "cpi_sporting", "cpi_footwear", "cpi_apparel", "basket", "ticket_minus_basket", "n_months"]); w.writerows(out)
for o in out: print(o)
covid = {"Q1FY20", "Q2FY20", "Q3FY20", "Q4FY20", "Q1FY21", "Q2FY21", "Q3FY21", "Q4FY21"}
nc = [o for o in out if o[0] not in covid]
sp = [o[6] for o in nc]
print("non-COVID n=%d mean spread %.2f median %.2f" % (len(sp), st.mean(sp), st.median(sp)))
xs = [o[5] for o in nc]; ys = [o[1] for o in nc]
mx, my = st.mean(xs), st.mean(ys)
b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
a = my - b * mx
corr = st.correlation(xs, ys)
print("OLS ticket = %.2f + %.2f * basket ; r = %.2f" % (a, b, corr))
for lab, rng in [("FY18-19", ("FY18", "FY19")), ("FY22-23", ("FY22", "FY23")), ("FY24-26", ("FY24", "FY25", "FY26"))]:
    s = [o for o in nc if o[0][-4:] in rng]
    if s: print(lab, "ticket %.2f basket %.2f spread %.2f" % (st.mean(o[1] for o in s), st.mean(o[5] for o in s), st.mean(o[6] for o in s)))
