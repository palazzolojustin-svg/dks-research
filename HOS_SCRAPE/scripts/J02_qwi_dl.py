import subprocess,pandas as pd,os,sys
sts="oh nj fl tx ga az al nc va ks ny de ok pa ma nh il ia mn tn la co".split()
cols=["geography","industry","sex","agegrp","ownercode","race","ethnicity","education","firmage","firmsize","year","quarter","Emp","EmpEnd","HirA","Sep","FrmJbC","EarnBeg"]
for s in sts:
    f=f"raw/J02/qwi_{s}.csv.gz"; o=f"data/J02_qwi_{s}_4591.csv"
    if os.path.exists(o): continue
    subprocess.run(["curl","-s","-o",f,f"https://lehd.ces.census.gov/data/qwi/latest_release/{s}/qwi_{s}_sa_f_gc_n4_op_u.csv.gz"])
    parts=[]
    try:
        for ch in pd.read_csv(f,usecols=lambda c:c in cols,dtype=str,chunksize=500000):
            parts.append(ch[(ch.industry=="4591")&(ch.sex=="0")&(ch.agegrp=="A00")&(ch.race=="A0")&(ch.ethnicity=="A0")&(ch.education=="E0")&(ch.firmage=="0")&(ch.firmsize=="0")])
        d=pd.concat(parts);d.to_csv(o,index=False)
        print(s,len(d),"last",d.year.max(),d[d.year==d.year.max()].quarter.max(),flush=True)
    except Exception as e: print(s,"ERR",e,flush=True)
    os.remove(f)
print("DONE")
