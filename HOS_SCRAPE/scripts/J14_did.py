import pandas as pd, numpy as np
C=pd.read_csv('data/J14_cbp_county_4511.csv')
ev=pd.read_csv('../THESIS_SCRAPE/raw/B5_hos_events.csv',encoding='utf-8-sig'); ev['fips']=ev.fips.astype(int)
ev['od']=pd.to_datetime(ev.open_date)
P=C.pivot(index='fips',columns='yr',values='ap'); E=C.pivot(index='fips',columns='yr',values='emp'); N=C.pivot(index='fips',columns='yr',values='est')
# control: counties with emp>=100 all years 2019-2023
ctl=E.index[(E[[2019,2020,2021,2022,2023]].min(axis=1)>=100)]
print('controls',len(ctl))
rows=[]
for _,e in ev[ev.od.dt.year<=2023].iterrows():
    y=e.od.year; f=e.fips
    if f not in P.index: continue
    frac=(12-e.od.month+1-(e.od.day>15))/12  # approx share of opening year after open
    # payroll growth y-1 -> y vs controls; and y-1 -> y+1 when available
    g=lambda a,b,x: (x.loc[:,b]/x.loc[:,a]-1)
    ge=P.loc[f,y]/P.loc[f,y-1]-1
    gc=(P.loc[ctl,y]/P.loc[ctl,y-1]-1)
    gcm=gc.median()
    pct=(gc<ge).mean()*100
    excess=(ge-gcm)*P.loc[f,y-1]   # $K excess payroll in opening year
    ann=excess/frac if frac>0 else np.nan
    wage=P.loc[f,y-1]/E.loc[f,y-1]  # $K per job (annual payroll per March job)
    # emp: Mar y-1 vs Mar y+? 
    e0=E.loc[f,y-1]; e1=E.loc[f,y] if y<=2023 else np.nan
    r=dict(store=e.store,city=e.city,open=e.open_date,type=e.type[:20],ap_prev=P.loc[f,y-1],ap_open_yr=P.loc[f,y],g_cty=ge*100,g_ctl_med=gcm*100,pctile=pct,excess_K=excess,frac=frac,annual_excess_K=ann,wage_K=wage,jobs_equiv=ann/wage if wage else np.nan)
    if y+1<=2023: r['ap_next']=P.loc[f,y+1]; r['g_next_vs_prev']=(P.loc[f,y+1]/P.loc[f,y-1]-1)*100; r['ctl_next']=(P.loc[ctl,y+1]/P.loc[ctl,y-1]-1).median()*100
    rows.append(r)
R=pd.DataFrame(rows); R.to_csv('data/J14_did_payroll.csv',index=False)
pd.set_option('display.width',250,'display.max_columns',30)
print(R.round(1).to_string(index=False))
# emp March change next-year vs controls for 2021/2022 openers
for f,n,y in [(36069,'Victor',2021),(47093,'Knox',2021),(27053,'Hennepin',2022)]:
    print(n,'Mar emp',{k:E.loc[f,k] for k in range(y-1,2024)},'ctl med growth y-1->y+1',((E.loc[ctl,y+1]/E.loc[ctl,y]-1).median()*100).round(1) if y+1<=2023 else '')
