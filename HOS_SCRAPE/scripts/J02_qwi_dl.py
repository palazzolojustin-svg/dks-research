import subprocess,pandas as pd,os,sys
sts="ny tn mn tx ia nc va il pa ma de fl ok nh oh la nj ks az ga al co".split()
cols=["geography","industry","sex","agegrp","year","quarter","Emp","EmpEnd","HirA","Sep","FrmJbC","EarnBeg"]
for s in sts:
    f=f"raw/J02/qwi_{s}.csv.gz"; o=f"data/J02_qwi_{s}_4511.csv"
    if os.path.exists(o): continue
    subprocess.run(["curl","-s","-o",f,f"https://lehd.ces.census.gov/data/qwi/latest_release/{s}/qwi_{s}_sa_f_gc_n4_op_u.csv.gz"])
    parts=[]
    try:
        for ch in pd.read_csv(f,usecols=lambda c:c in cols,dtype={"geography":str,"industry":str,"agegrp":str},chunksize=500000):
            parts.append(ch[(ch.industry=="4511")&(ch.sex==0)&(ch.agegrp=="A00")])
        d=pd.concat(parts);d.to_csv(o,index=False)
        print(s,len(d),"last",int(d.year.max()),int(d[d.year==d.year.max()].quarter.max()),flush=True)
    except Exception as e: print(s,"ERR",e,flush=True)
    os.remove(f)
print("DONE")
