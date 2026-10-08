import sys,os,subprocess,pandas as pd
s=sys.argv[1]; f=f"raw/K1/qwi_{s}.csv.gz"; o=f"data/K1_qwi_{s}_fs.csv"
os.makedirs("raw/K1",exist_ok=True)
if os.path.exists(o): sys.exit()
src=f"raw/J02/qwi_{s}.csv.gz" if s in("ga","tx") else f
if s not in("ga","tx"):
    for i in range(6):
        r=subprocess.run(["curl","-s","-C","-","-f","-o",f,f"https://lehd.ces.census.gov/data/qwi/latest_release/{s}/qwi_{s}_sa_f_gc_n4_op_u.csv.gz"])
        if r.returncode==0: break
cols=["geography","industry","sex","agegrp","ownercode","race","ethnicity","education","firmage","firmsize","year","quarter","Emp","HirA","Sep","FrmJbC"]
parts=[]
try:
    for ch in pd.read_csv(src,dtype=str,chunksize=500000,usecols=lambda c:c in cols):
        m=(ch.industry=="4591")&(ch.sex=="0")&(ch.agegrp=="A00")&(ch.race=="A0")&(ch.ethnicity=="A0")&(ch.education=="E0")&((ch.firmage=="0")|(ch.firmsize=="0"))
        parts.append(ch[m])
except Exception as e: print(s,"ERR",e,flush=True)
d=pd.concat(parts);d.to_csv(o,index=False)
print(s,len(d),d.year.max(),d[d.year==d.year.max()].quarter.max(),sorted(d.firmsize.unique()),sorted(d.firmage.unique()),flush=True)
if s not in("ga","tx") and os.path.exists(f): os.remove(f)
