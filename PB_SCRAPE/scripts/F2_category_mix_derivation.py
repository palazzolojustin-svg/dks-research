r"""F2_category_mix_derivation.py
Derives DICK'S-segment (ex-Foot Locker) category sales from DKS 10-K/10-Q revenue disaggregation
(which is consolidated, not split by segment) by subtracting an assumed Foot Locker category mix,
and computes owned-brand penetration of non-footwear sales FY21-FY25.
Inputs are hard-coded from WORKING_NOTES (W01 10-K FY25 Net sales by category; W02 FY21-FY23; W04 10-Q Note 6/8)
and C01_SYNTHESIS_B (segment sales). Rerun: python PB_SCRAPE\scripts\F2_category_mix_derivation.py
Update each quarter by appending the new 10-Q Note 6 category row and FL segment sales.
Key assumption: FL sales are ~84% footwear / 16% apparel & accessories (FL FY2024 10-K), ~0 hardlines,
FL 'other' small; sensitivity at 80% and 88%. FL accessories assumed booked in DKS 'Apparel' (unverified).
"""
import csv
OUT=r"C:\Users\palaz\Downloads\DKS_RESEARCH\PB_SCRAPE\raw\F2_dicks_segment_category_derivation.csv"
# consolidated category $M: footwear, hardlines, apparel, other, total ; FL segment sales ; DICK'S segment sales
P={
 "FY21":dict(fw=2562.8,hl=5407.9,ap=4131.2,ot=191.5,tot=12293.4,fl=0,dk=12293.4),
 "FY22":dict(fw=2979.1,hl=4952.2,ap=4218.1,ot=218.8,tot=12368.2,fl=0,dk=12368.2),
 "FY23":dict(fw=3388.7,hl=4915.5,ap=4329.8,ot=350.4,tot=12984.4,fl=0,dk=12984.4),
 "FY24":dict(fw=3829.0,hl=4899.3,ap=4425.4,ot=289.1,tot=13442.8,fl=0,dk=13442.8),
 "FY25":dict(fw=6888.0,hl=5048.3,ap=4895.4,ot=383.4,tot=17215.1,fl=3106.2,dk=14108.9),
 "Q1FY25":dict(fw=998.3,hl=1192.9,ap=884.7,ot=98.8,tot=3174.7,fl=0,dk=3174.7),
 "Q1FY26":dict(fw=2605.1,hl=1326.6,ap=1109.5,ot=123.3,tot=5164.5,fl=1787.1,dk=3377.4),
 "Q2FY25":dict(fw=1087.7,hl=1471.5,ap=1008.5,ot=78.9,tot=3646.6,fl=0,dk=3646.6),
 "Q2FY26":dict(fw=2616.1,hl=1552.3,ap=1299.4,ot=119.0,tot=5586.8,fl=1736.9,dk=3849.9),
 "1HFY25":dict(fw=2086.0,hl=2664.4,ap=1893.2,ot=177.7,tot=6821.3,fl=0,dk=6821.3),
 "1HFY26":dict(fw=5221.2,hl=2878.9,ap=2408.9,ot=242.3,tot=10751.3,fl=3524.0,dk=7227.3),
}
PL={"FY21":0.14,"FY22":0.14,"FY23":0.13,"FY24":0.13,"FY25":0.13} # Wells Fargo Exh.85 / 10-K risk factor (~13% FY25)
PLD={"FY23":1600,"FY24":1700,"FY25":1800} # mgmt $M
rows=[]
for fwshare in (0.80,0.84,0.88):
    for k,v in P.items():
        flfw=v["fl"]*fwshare; flap=v["fl"]-flfw
        d=dict(period=k,fl_fw_share=fwshare,dk_fw=v["fw"]-flfw,dk_hl=v["hl"],dk_ap=v["ap"]-flap)
        d["dk_nonfw"]=d["dk_hl"]+d["dk_ap"]
        if k in PL:
            d["pl_pct_sales"]=PL[k]; d["pl_usd_from_pct"]=PL[k]*v["dk"]
            d["pl_share_of_nonfw_pct"]=round(100*PL[k]*v["dk"]/d["dk_nonfw"],1)
            if k in PLD: d["pl_share_of_nonfw_mgmt$"]=round(100*PLD[k]/d["dk_nonfw"],1)
        rows.append(d)
def g(p,f,key):
    return [r for r in rows if r["period"]==p and r["fl_fw_share"]==f][0][key]
print("y/y growth of DICK'S-segment categories (derived)")
for f in (0.80,0.84,0.88):
    for a,b in (("FY25","FY24"),("Q1FY26","Q1FY25"),("Q2FY26","Q2FY25"),("1HFY26","1HFY25")):
        print(f"FL fw {f:.0%} {a} vs {b}: footwear {g(a,f,'dk_fw')/g(b,f,'dk_fw')-1:+.1%}  apparel {g(a,f,'dk_ap')/g(b,f,'dk_ap')-1:+.1%}  hardlines {g(a,f,'dk_hl')/g(b,f,'dk_hl')-1:+.1%}  non-fw {g(a,f,'dk_nonfw')/g(b,f,'dk_nonfw')-1:+.1%}")
print("\nOwned-brand share of DICK'S non-footwear (hardlines+apparel) sales")
for k in ("FY21","FY22","FY23","FY24","FY25"):
    r=[r for r in rows if r["period"]==k and r["fl_fw_share"]==0.84][0]
    print(k, "fw share of DICK'S sales %.1f%%"%(100*r["dk_fw"]/P[k]["dk"]), "| PL%%-based %.1f%%"%r["pl_share_of_nonfw_pct"], "| mgmt$-based", r.get("pl_share_of_nonfw_mgmt$","-"))
keys=sorted({k for r in rows for k in r})
with open(OUT,"w",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=keys); w.writeheader(); w.writerows(rows)
print("wrote",OUT)

# ---- INFERENCE scenario: owned-brand % of DICK'S sales if footwear stalls (footwear "hangover") ----
print("\nScenario (INFERENCE): DICK'S sales, footwear $, non-fw penetration -> owned % of DICK'S sales")
base_fw=P["FY25"]["fw"]-P["FY25"]["fl"]*0.84; base_pen=1800/(P["FY25"]["dk"]-base_fw-P["FY25"]["ot"]+0)  # ~19.1% (other mostly DICK'S)
for yr,sales,fw_g,pen_add in (("FY26E",14600,0.00,0.005),("FY27E",15040,0.00,0.010),("FY26E-flatpen",14600,0.00,0.0),("FY27E-flatpen",15040,0.00,0.0),("FY27E-fw+8%/yr",15040,0.08,0.0)):
    n=1 if yr.startswith("FY26") else 2
    fw=base_fw*(1+fw_g)**n; other=420
    nonfw=sales-fw-other; pen=base_pen+pen_add
    print(f"{yr}: sales {sales}, footwear {fw:.0f}, non-fw {nonfw:.0f}, penetration {pen:.1%} -> owned ${nonfw*pen:.0f}M = {nonfw*pen/sales:.1%} of DICK'S sales")
