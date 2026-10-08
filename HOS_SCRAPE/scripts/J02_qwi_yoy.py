import pandas as pd,glob,numpy as np
ev=pd.read_csv("../THESIS_SCRAPE/raw/B5_hos_events.csv",dtype={"fips":str},encoding="utf-8-sig");ev["fips"]=ev.fips.str.zfill(5)
q=pd.concat([pd.read_csv(f,dtype={"geography":str}) for f in glob.glob("data/J02_qwi_*_4591.csv")])
for c in ["Emp","HirA","Sep"]: q[c]=pd.to_numeric(q[c],errors="coerce")
q["t"]=q.year*4+q.quarter-1; q["st"]=q.geography.str[:2]
q=q.set_index(["geography","t"])
evf=set(ev.fips)
rows=[]
for _,e in ev.iterrows():
    t0=int(e.open_q[:4])*4+int(e.open_q[-1])-1
    st=e.fips[:2]
    cs=q[(q.st==st)&(~q.index.get_level_values(0).isin(evf))].reset_index()
    for k in range(0,4):
        t=t0+k
        try: a=q.loc[(e.fips,t)];b=q.loc[(e.fips,t-4)]
        except KeyError: continue
        if np.isnan(a.Emp) or np.isnan(b.Emp): continue
        # control: counties with non-null in both periods
        x=cs[cs.t==t].set_index("geography");y=cs[cs.t==t-4].set_index("geography")
        j=x.join(y,lsuffix="n",rsuffix="o").dropna(subset=["Empn","Empo"])
        g=j.Empn.sum()/j.Empo.sum() if len(j)>3 else np.nan
        gh=(j.HirAn.sum()/j.HirAo.sum()) if len(j)>3 else np.nan
        exE=a.Emp-b.Emp*g; exH=a.HirA-b.HirA*gh
        rows.append((e.city,e.open_q,k,int(b.Emp),int(a.Emp),round(g,3),round(exE),int(b.HirA) if not np.isnan(b.HirA) else None,int(a.HirA) if not np.isnan(a.HirA) else None,round(exH) if not np.isnan(exH) else None,len(j)))
o=pd.DataFrame(rows,columns=["city","open_q","k","Emp_ly","Emp","ctl_yoy","excessEmp_vs_ctl","Hir_ly","Hir","excessHir","nctl"])
pd.set_option("display.width",200);print(o.to_string());o.to_csv("data/J02_qwi_yoy.csv",index=False)
