import pandas as pd,numpy as np
pd.set_option('display.width',250)
L=pd.read_pickle('raw/J03/L.pkl')
ev=pd.read_csv('../THESIS_SCRAPE/raw/B5_hos_events.csv',encoding='utf-8-sig',dtype={'fips':str}); ev['fips']=ev.fips.str.zfill(5)
hosf=set(ev.fips); ev=ev[ev.open_q>='2025Q3']
piv=L.pivot_table(index='f',columns='m',values='emp',aggfunc='sum'); dis=L.pivot_table(index='f',columns='m',values='disc',aggfunc='min')
M=sorted(piv.columns)
ctrl=[f for f in piv.index if f not in hosf and dis.loc[f,M].fillna(False).all() and piv.loc[f,M].min()>0]
C=piv.loc[ctrl,M].sum()
def yoy(f,m): return piv.loc[f,m]-piv.loc[f,m-12]*C[m]/C[m-12]
def pre6(f,t0,m):
    bm=[t0*3-6+i for i in range(6)]; b=np.mean([piv.loc[f,x]/C[x] for x in bm]); return piv.loc[f,m]-b*C[m]
mo=lambda y,mm:y*12+mm-1
# noise: control counties, same estimators, Feb-Mar 2026 avg; by base-size bin
def noise(fn):
    out=[]
    for f in ctrl:
        out.append((piv.loc[f,mo(2025,1):mo(2025,12)].mean(),np.mean([fn(f,mo(2026,2)),fn(f,mo(2026,3))])))
    d=pd.DataFrame(out,columns=['base','x']);d['bin']=pd.cut(d.base,[0,100,300,800,2000,1e5])
    return d.groupby('bin',observed=True).x.agg(['count','mean','std'])
print('YOY noise Feb-Mar26 (controls)');print(noise(yoy).round(1))
t0=lambda e:int(e.open_q[:4])*4+int(e.open_q[-1])-1
rows=[]
for _,e in ev.iterrows():
    f=e.fips;t=t0(e);o=pd.Timestamp(e.open_date)
    om=mo(o.year,o.month)
    post=[m for m in range(om,mo(2026,3)+1) if m>=t*3 and dis.loc[f,m]==True and dis.loc[f,m-12]==True]
    try:
        y_last2=np.mean([yoy(f,mo(2026,2)),yoy(f,mo(2026,3))]); p_last2=np.mean([pre6(f,t,mo(2026,2)),pre6(f,t,mo(2026,3))])
        y_all=np.mean([yoy(f,m) for m in post]); 
    except Exception as ex: y_last2=p_last2=y_all=np.nan
    rows.append(dict(city=e.city,open=e.open_date,n_post_mo=len(post),yoy_postavg=y_all,yoy_FebMar=y_last2,pre6_FebMar=p_last2))
R=pd.DataFrame(rows).set_index('city')
# wages & estabs from quarterly
Q=L.groupby(['f','y','qtr']).agg(wag=('wag','first'),est=('est','first'),disc=('disc','min')).reset_index()
Q['t']=Q.y*4+Q.qtr-1
W=Q.pivot_table(index='f',columns='t',values='wag');E=Q.pivot_table(index='f',columns='t',values='est')
CW=W.loc[ctrl].sum();CE=E.loc[ctrl].sum()
w=[];es=[]
for _,e in ev.iterrows():
    f=e.fips;tt=2026*4
    try:
        ex=W.loc[f,tt]-W.loc[f,tt-4]*CW[tt]/CW[tt-4]
        ee=E.loc[f,tt]-E.loc[f,tt-4]*CE[tt]/CE[tt-4]
        e0=E.loc[f,tt-4]
    except: ex=ee=e0=np.nan
    w.append(ex/1e6*4); es.append((E.loc[f,tt-4],E.loc[f,tt],ee))
R['wag_exc_2026Q1_annualized_$M']=w
R['estabs_25Q1,26Q1,excess']=es
print(R.round(1).to_string())
R.to_csv('data/J03_robust.csv')
# also estab count + size table 2025Q2 vs 2026Q1
for _,e in ev.iterrows():
    f=e.fips
    print(e.city,[ (int(E.loc[f,t]) if t in E.columns else None) for t in (2025*4+1,2025*4+3,2026*4)], 'avg size 25Q2/25Q4/26Q1',[round(L[(L.f==f)&(L.y==y)&(L.qtr==q)].emp.iloc[2]/max(1,E.loc[f,y*4+q-1]),1) for y,q in ((2025,2),(2025,4),(2026,1))])
