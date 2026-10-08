import sys,os,subprocess,pandas as pd
s,k=sys.argv[1],sys.argv[2]   # state, fs|fa
f=f"raw/K1/qwi_{s}_{k}.csv.gz"; o=f"data/K1_qwi_{s}_{k}_gcns.csv"
os.makedirs("raw/K1",exist_ok=True)
if os.path.exists(o): sys.exit()
for i in range(8):
    r=subprocess.run(["curl","-s","-C","-","-f","-o",f,f"https://lehd.ces.census.gov/data/qwi/latest_release/{s}/qwi_{s}_sa_{k}_gc_ns_op_u.csv.gz"])
    if r.returncode==0: break
cols=["geography","sex","agegrp","ownercode","race","ethnicity","education","firmage","firmsize","year","quarter","Emp","HirA","Sep","FrmJbC"]
parts=[]
for ch in pd.read_csv(f,dtype=str,chunksize=500000,usecols=cols):
    parts.append(ch[(ch.sex=="0")&(ch.agegrp=="A00")&(ch.race=="A0")&(ch.ethnicity=="A0")&(ch.education=="E0")])
d=pd.concat(parts);d.to_csv(o,index=False)
print(s,k,len(d),d.year.max(),sorted(d.firmsize.unique()),sorted(d.firmage.unique()),flush=True)
os.remove(f)
