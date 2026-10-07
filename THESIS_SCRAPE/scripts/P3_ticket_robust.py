r"""P3: robustness of DKS ticket vs CPI basket (contemporaneous / lag1, subsamples) + scenario $ variance.
Rerun: python THESIS_SCRAPE\scripts\P3_ticket_robust.py (needs raw\P3_ticket_vs_cpi_quarterly.csv)."""
import numpy as np, pandas as pd
RAW=r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw"
d=pd.read_csv(RAW+r"\P3_ticket_vs_cpi_quarterly.csv",index_col=0)
d["basket_l1"]=d["basket"].shift(1)
d=d[~d.index.str.contains("FY20|FY21")].dropna(subset=["ticket"])
def ols(sub,x):
    s=sub.dropna(subset=[x]); X=np.c_[np.ones(len(s)),s[x]]; b=np.linalg.lstsq(X,s.ticket,rcond=None)[0]
    r2=1-((s.ticket-X@b)**2).sum()/((s.ticket-s.ticket.mean())**2).sum(); return b,r2,len(s)
for lab,sub in [("FY16-26",d),("FY16-19",d[d.index.str.contains("FY1[6-9]")]),("FY22-26",d[d.index.str.contains("FY2[2-6]")])]:
    for x in ["basket","basket_l1"]:
        b,r2,n=ols(sub,x); print(f"{lab} {x}: ticket={b[0]:.2f}+{b[1]:.2f}x R2={r2:.2f} n={n}")
# first differences: does a change in CPI basket move ticket?
dd=d[["ticket","basket"]].diff().dropna(); print("corr of q/q changes", dd.corr().iloc[0,1].round(2))
# scenarios vs consensus
cons={"Q3 FY26":(1.25,3437.0),"Q4 FY26":(1.00,4144.0),"Q1 FY27":(1.00,3480.4),"Q2 FY27":(1.00,3967.3)}
basket={"Q3 FY26":3.81,"Q4 FY26":3.72,"Q1 FY27":2.02,"Q2 FY27":0.54}  # zero-momentum CPI path (P3_ticket_projection.csv)
rows=[]
for q,(ct,rev) in cons.items():
    sc={"A OLS (no CPI link)":1.77,"B mix drift 1.3 + 0.5x basket":1.3+0.5*basket[q],"C persistence (Q2 FY26 actual 3.6)":3.6}
    for k,v in sc.items():
        gap=v-ct; drev=gap/100*rev
        rows.append(dict(quarter=q,scenario=k,ticket=round(v,2),cons_ticket=ct,gap_pt=round(gap,2),rev_usdM=round(drev,1),eps_fl25=round(drev*0.25*0.00814,3)))
r=pd.DataFrame(rows); r.to_csv(RAW+r"\P3_ticket_scenarios.csv",index=False); print(r.to_string())
print(r.groupby("scenario")[["rev_usdM","eps_fl25"]].sum().round(2))

