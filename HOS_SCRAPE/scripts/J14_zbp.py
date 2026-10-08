import pandas as pd, re, glob, sys
R='raw/J14/'
ev=pd.read_csv('../THESIS_SCRAPE/raw/B5_hos_events.csv',encoding='utf-8-sig')
yrs=[18,19,20,21,22,23]
def load(y):
    f=glob.glob(f'{R}zbp{y}/*.txt')[0]
    d=pd.read_csv(f,dtype=str,encoding='latin-1')
    d['yr']=2000+y
    return d
Z={y:load(y) for y in yrs}
# sporting goods naics rows
def sg(d):
    n=d['naics'].str.replace('/','').str.replace('-','')
    return d[n.isin(['4511','45111','451110','4591','45911','459110'])]
# zip->city/state/county from 2023
z23=Z[23][['zip','city','stabbr','cty_name']].drop_duplicates('zip')
cols=['n<5','n5_9','n10_19','n20_49','n50_99','n100_249','n250_499','n500_999','n1000']
out=[]
for y in yrs:
    s=sg(Z[y]).copy()
    s=s.merge(z23,on='zip',how='left',suffixes=('_x',''))
    s['naics6']=s['naics'].str.replace('/','').str.replace('-','')
    # prefer most detailed
    s['L']=s['naics6'].str.len()
    s=s.sort_values('L').drop_duplicates('zip',keep='last')
    out.append(s)
A=pd.concat(out)
for c in cols+['est']:
    A[c]=pd.to_numeric(A[c],errors='coerce').fillna(0).astype(int)
A['big']=A[['n100_249','n250_499','n500_999','n1000']].sum(axis=1)
A.to_csv('data/J14_zbp_sportinggoods_all.csv',index=False)
print(A.groupby('yr').agg(zips=('zip','count'),big=('big','sum')))
# big zips panel
big=A[A.big>0].pivot_table(index=['zip','city','stabbr'],columns='yr',values='big',aggfunc='sum').fillna(0).astype(int)
big.to_csv('data/J14_zbp_big_sporting_zips.csv')
print(len(big))
# match HoS cities
def norm(s): return re.sub(r'\(.*\)','',str(s)).strip().upper()
rows=[]
for _,e in ev.iterrows():
    c=norm(e.city); 
    names=[c]+({'HARRIS':['HOUSTON','KATY'],'BOSTON':['BOSTON'],'COLUMBUS':['COLUMBUS','LEWIS CENTER','POWELL'],'LIVE OAK':['LIVE OAK','SAN ANTONIO','SELMA'],'DALLAS':['DALLAS'],'PITTSBURGH':['PITTSBURGH'],'MIAMI':['MIAMI'],'TAMPA':['TAMPA'],'WILMINGTON':['WILMINGTON'],'OKLAHOMA CITY':['OKLAHOMA CITY'],'TULSA':['TULSA']}.get(c,[]))
    m=A[(A.stabbr==e.state)&(A.city.str.upper().isin(names))]
    zips=sorted(m.zip.unique())
    rows.append((e.store,e.city,e.state,e.open_q,zips))
print(len(rows))
import pickle;pickle.dump(rows,open(R+'rows.pkl','wb'))
# show per event: for zips in city, 100+ counts and est by year
for st,city,s,oq,zips in rows:
    sub=A[A.zip.isin(zips)]
    if sub.empty: print(st,city,s,oq,'NO ZIP SPORTING ROWS'); continue
    g=sub.groupby('yr').agg(est=('est','sum'),b100=('n100_249','sum'),b250=('n250_499','sum'),b50=('n50_99','sum'),z=('zip','count'))
    print(f'{st} {city} {s} open {oq} zips{len(zips)} | '+' '.join(f"{y}:e{r.est}/50:{r.b50}/100:{r.b100}/250:{r.b250}" for y,r in g.iterrows()))
