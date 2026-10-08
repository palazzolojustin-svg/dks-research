import pandas as pd,glob,numpy as np
ev=pd.read_csv("../THESIS_SCRAPE/raw/B5_hos_events.csv",dtype={"fips":str},encoding="utf-8-sig")
ev["fips"]=ev.fips.str.zfill(5)
extra=pd.DataFrame([{"store":1,"city":"Arlington TX","state":"TX","fips":"48439","open_q":"2026Q2"}])
ev=pd.concat([ev,extra]);ev=ev.drop_duplicates("fips" ,keep="first") if False else ev
q=pd.concat([pd.read_csv(f,dtype={"geography":str}) for f in glob.glob("data/J02_qwi_*_4591.csv")])
for c in ["Emp","EmpEnd","HirA","Sep","FrmJbC","EarnBeg"]: q[c]=pd.to_numeric(q[c],errors="coerce")
q["t"]=q.year*4+q.quarter-1
q["st"]=q.geography.str[:2]
rows=[]
for _,e in ev.iterrows():
    oq=e.open_q; t0=int(oq[:4])*4+int(oq[-1])-1
    c=q[q.geography==e.fips].set_index("t")
    ctl=q[(q.st==e.fips[:2])&(~q.geography.isin(ev.fips))].groupby("t")[["Emp","HirA"]].sum()
    if c.empty: rows.append((e.city,oq,"nodata"));continue
    last=c.index[c.Emp.notna()].max() if c.Emp.notna().any() else None
    def E(t): return c.Emp.get(t,np.nan)
    base=np.nanmean([E(t0-1),E(t0-2),E(t0-3),E(t0-4)])
    hb=np.nanmean([c.HirA.get(t0-k,np.nan) for k in (1,2,3,4)])
    post=[E(t0+k) for k in range(0,5)]
    def idx(t):
        try: return ctl.Emp[t]/np.nanmean([ctl.Emp.get(t0-k) for k in (1,2,3,4)])
        except: return np.nan
    lastk=(last-t0) if last is not None else None
    rows.append((e.city,oq,round(base,0),[None if np.isnan(x) else int(x) for x in post],round(hb,0),
      [None if np.isnan(c.HirA.get(t0+k,np.nan)) else int(c.HirA.get(t0+k)) for k in range(0,3)],lastk,
      round(E(last)-base,0) if last is not None else None, round(idx(last),3) if last is not None else None))
out=pd.DataFrame(rows,columns=["city","open_q","base_emp(k-4..-1)","Emp k0..k4","base_hires","HirA k0..k2","last_k","dEmp_last_vs_base","ctl_idx_last"])
pd.set_option("display.width",250,"display.max_colwidth",60);print(out.to_string())
out.to_csv("data/J02_qwi_event_table.csv",index=False)
