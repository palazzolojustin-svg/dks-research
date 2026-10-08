import pandas as pd,glob,numpy as np
ev=pd.read_csv("../THESIS_SCRAPE/raw/B5_hos_events.csv",dtype={"fips":str},encoding="utf-8-sig");ev["fips"]=ev.fips.str.zfill(5)
sm=pd.read_csv("../THESIS_SCRAPE/raw/B5_event_summary.csv").set_index("city")
j2=pd.read_csv("data/J02_qwi_yoy.csv")
def load(k):
    fs=glob.glob(f"data/K1_qwi_*_{k}_gcns.csv")
    q=pd.concat([pd.read_csv(f,dtype={"geography":str,"firmage":str,"firmsize":str}) for f in fs]);q=q[q.ownercode=="A05"].drop_duplicates(["geography","year","quarter","firmage","firmsize"]);q["Emp"]=pd.to_numeric(q.Emp,errors="coerce")
    q["t"]=q.year*4+q.quarter-1;q["st"]=q.geography.str[:2];return q
FS=load("fs")
import os
try: FA=load("fa")
except Exception: FA=FS[FS.Emp<-1]
cuts={"all":(FS,"0","0"),"size500":(FS,"0","5"),"age11":(FA,"5","0"),"age0_3":(FA,"1","0")}
evf=set(ev.fips);rows=[];noise=[]
for name,(q,fa,fs) in cuts.items():
    dd=q[(q.firmage==fa)&(q.firmsize==fs)][["geography","t","st","Emp"]].dropna()
    d=dd.set_index(["geography","t"]).Emp.to_dict()
    sts=set(dd.st)
    for _,e in ev.iterrows():
        if e.fips[:2] not in sts:continue
        t0=int(e.open_q[:4])*4+int(e.open_q[-1])-1;st=e.fips[:2]
        cs=dd[(dd.st==st)&(~dd.geography.isin(evf))]
        for k in range(0,4):
            t=t0+k
            if (e.fips,t) not in d or (e.fips,t-4) not in d:continue
            x=cs[cs.t==t].set_index("geography").Emp;y=cs[cs.t==t-4].set_index("geography").Emp
            j=pd.concat([x.rename("n"),y.rename("o")],axis=1).dropna()
            if len(j)<4:continue
            g=j.n.sum()/j.o.sum();ex=d[(e.fips,t)]-d[(e.fips,t-4)]*g
            # placebo noise: control counties of similar size (0.5x-2x)
            b=d[(e.fips,t-4)];m=j[(j.o>b*.5)&(j.o<b*2)]
            sd=np.std(m.n-m.o*g,ddof=1) if len(m)>=4 else np.nan
            rows.append((name,e.city,e.open_q,k,d[(e.fips,t-4)],d[(e.fips,t)],round(g,3),ex,sd,len(m)))
o=pd.DataFrame(rows,columns=["cut","city","open_q","k","Emp_ly","Emp","ctl_yoy","excess","placebo_sd","n_placebo"])
o.to_csv("data/K1_qwi_cut_yoy_long.csv",index=False)
nn={"Boston(Prudential)","Pittsburgh(Ross Park)","Jersey City","Glendale","Live Oak(San Antonio)"}
rl={"Minnetonka","Johnson City","Davenport","Champaign","Scranton","Tampa(Intl Plaza)","Harris(Baybrook+Katy)","Fayetteville","Amherst"}
rlx=rl|{"Freehold","Brandon","Dallas(Galleria)","Victor","Knoxville"}
res=[]
for city,g in ev.groupby("city",sort=False):
    r={"city":city,"open_q":g.open_q.iloc[0],"group":"net-new" if city in nn else "relocation" if city in rl else "reloc_ext" if city in rlx else "other"}
    for cn in cuts:
        s=o[(o.cut==cn)&(o.city==city)].set_index("k")
        r[f"{cn}_nq"]=len(s)
        for k in (0,1,3):r[f"{cn}_k{k}"]=s.excess.get(k,np.nan)
        r[f"{cn}_mean"]=s.excess.mean() if len(s) else np.nan
        r[f"{cn}_base"]=s.Emp_ly.iloc[0] if len(s) else np.nan
        r[f"{cn}_psd"]=s.placebo_sd.mean() if len(s) else np.nan
    a=j2[j2.city==city].set_index("k").excessEmp_vs_ctl
    r["J02_4591_k0"]=a.get(0,np.nan);r["J02_4591_k1"]=a.get(1,np.nan);r["J02_4591_mean"]=a.mean() if len(a) else np.nan
    r["qcew_y1"]=sm.y1_jobs.get(city,np.nan)
    res.append(r)
R=pd.DataFrame(res)
for cn in ["size500","age11","J02_4591"]:
    c=f"{cn}_mean"
    R[f"{cn}_mean_$215K_M"]=R[c]*.215;R[f"{cn}_mean_$70K_M"]=R[c]*.07
R.to_csv("data/K1_qwi_cut_event_summary.csv",index=False)
pd.set_option("display.width",250,"display.max_rows",200)
print(R[["city","open_q","group","J02_4591_mean","J02_4591_k0","size500_nq","size500_base","size500_k0","size500_k1","size500_mean","size500_psd","age11_mean","age11_psd","qcew_y1"]].round(0).to_string())
rows=[]
for cn,c in [("J02_4591","J02_4591_mean"),("size500","size500_mean"),("age11","age11_mean"),("qcew_y1","qcew_y1"),("size500_k0","size500_k0"),("size500_k1","size500_k1")]:
    for gname,sel in [("net-new",R.group=="net-new"),("relocation(core J13)",R.group=="relocation"),("relocation(ext)",R.group.isin(["relocation","reloc_ext"])),("all events",R.group!="x")]:
        v=R.loc[sel,c].dropna()
        rows.append((cn,gname,len(v),v.mean(),v.median(),v.mean()*.215,v.mean()*.07,v.median()*.215,v.median()*.07))
P=pd.DataFrame(rows,columns=["measure","group","n","mean_jobs","median_jobs","mean_$M_215K","mean_$M_70K","med_$M_215K","med_$M_70K"])
P.to_csv("data/K1_pooled.csv",index=False);print(P.round(1).to_string())
