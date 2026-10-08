import requests,pandas as pd,io,gzip,sys
sts="ny tn mn tx ia nc va il pa ma de fl ok nh oh la nj ks az ga al co md mi wi".split()
out=[]
for s in sts:
    u=f"https://lehd.ces.census.gov/data/qwi/latest_release/{s}/qwi_{s}_sa_f_gc_n4_op_u.csv.gz"
    try:
        r=requests.get(u,timeout=300)
        if r.status_code!=200: print(s,"HTTP",r.status_code);continue
        df=pd.read_csv(io.BytesIO(r.content),compression="gzip",dtype={"geography":str,"industry":str,"agegrp":str},low_memory=False)
        d=df[(df.industry=="4511")&(df.sex==0)&(df.agegrp=="A00")]
        keep=[c for c in ["geography","year","quarter","Emp","EmpEnd","HirA","Sep","FrmJbC","EarnBeg","Payroll","sEmp","sHirA"] if c in d.columns]
        d=d[keep].copy();d["state"]=s;out.append(d)
        print(s,len(df),len(d),"last",int(d.year.max()),int(d[d.year==d.year.max()].quarter.max()),flush=True)
    except Exception as e: print(s,"ERR",e)
pd.concat(out).to_csv("data/J02_qwi_4511_counties.csv",index=False)
