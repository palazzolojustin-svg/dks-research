import pandas as pd,numpy as np,glob
pd.set_option('display.width',250)
fs=sorted(glob.glob('raw/J03/ind459110_*.csv'))
q=pd.concat([pd.read_csv(f,dtype={'area_fips':str}) for f in fs])
q=q[(q.own_code==5)&(q.agglvl_code==78)]  # county, private, NAICS 6-digit
q['t']=q.year*4+q.qtr-1
print(q.groupby(['year','qtr']).agg(n=('area_fips','size'),disc=('disclosure_code',lambda s:s.fillna('').eq('').sum())).tail(5))
ev=pd.read_csv('../THESIS_SCRAPE/raw/B5_hos_events.csv',encoding='utf-8-sig',dtype={'fips':str})
ev['fips']=ev.fips.str.zfill(5)
ev=ev[ev.open_q>='2025Q3']
hosf=set(pd.read_csv('../THESIS_SCRAPE/raw/B5_hos_events.csv',encoding='utf-8-sig',dtype={'fips':str}).fips.str.zfill(5))
q['disc']=q.disclosure_code.fillna('').eq('')
mc=['month1_emplvl','month2_emplvl','month3_emplvl']
# long monthly
rows=[]
for _,r in q.iterrows():
    for i,c in enumerate(mc):
        rows.append((r.area_fips,r.year,r.qtr,r.t*3+i,r[c],r.disc,r.qtrly_estabs,r.total_qtrly_wages))
L=pd.DataFrame(rows,columns=['f','y','qtr','m','emp','disc','est','wag'])
L.to_pickle('raw/J03/L.pkl')
# control: disclosed counties never HoS, present all months, size 20-3000 jobs
piv=L.pivot_table(index='f',columns='m',values='emp',aggfunc='sum'); dis=L.pivot_table(index='f',columns='m',values='disc',aggfunc='min')
M=sorted(piv.columns); ctrl=[f for f in piv.index if f not in hosf and dis.loc[f,M].fillna(False).all() and piv.loc[f,M].min()>0]
print('control counties',len(ctrl))
C=piv.loc[ctrl,M].sum()
base_m=lambda t0:[t0*3-6+i for i in range(6)]  # 6 months before open quarter
res=[]
for _,e in ev.iterrows():
    t0=int(e.open_q[:4])*4+int(e.open_q[-1])-1
    f=e.fips
    if f not in piv.index: print('missing',e.city); continue
    # seasonally-adjusted: ratio to control; baseline = mean ratio of 6 months before open qtr
    bm=base_m(t0)
    ratio=lambda m:piv.loc[f,m]/C[m]
    b=np.nanmean([ratio(m) for m in bm]); b3=piv.loc[f,bm].mean()
    ser={}
    for m in range(t0*3,t0*3+9):
        if m in M and not np.isnan(piv.loc[f,m]) and dis.loc[f,m] is not False and dis.loc[f,m]==True:
            ser[m]=piv.loc[f,m]-b*C[m]
    cal=lambda m:f'{m//12}-{(m%12)+1:02d}'
    res.append(dict(city=e.city,open=e.open_date,base_emp=round(b3),
        **{cal(m):round(v) if True else v for m,v in ser.items()}))
R=pd.DataFrame(res);print(R.to_string())
R.to_csv('data/J03_monthly_excess.csv',index=False)
# raw levels table last 15 months
lv=[]
for _,e in ev.iterrows():
    f=e.fips
    if f not in piv.index: continue
    s=piv.loc[f,[m for m in M if m>=2024*12+0]]
    d=dis.loc[f,s.index]
    lv.append(dict(city=e.city,fips=f,**{f'{m//12}-{m%12+1:02d}':(int(s[m]) if d[m] else 'S') for m in s.index if m>=2025*12+0}))
print(pd.DataFrame(lv).to_string())
