import requests,re,html,time,os,pandas as pd,json
from concurrent.futures import ThreadPoolExecutor
H={'User-Agent':'Research palazzolojustin@gmail.com'}
d=pd.read_csv('data/M02_fts_hits.csv')
first=sorted(d.center.unique())[:20]
x=d[d.center.isin(first)&d.form.isin(['FWP','424H','424B2','424B3','424B5'])].copy()
x['key']=x.id
docs=x.drop_duplicates('id')
def get(r):
    acc,fn=r['id'].split(':'); p=f"raw/M02/{acc}_{fn}"
    if not os.path.exists(p):
        u=f"https://www.sec.gov/Archives/edgar/data/{r['cik']}/{acc.replace('-','')}/{fn}"
        for _ in range(3):
            try: t=requests.get(u,headers=H,timeout=60).text;break
            except Exception: time.sleep(1);t=''
        open(p,'w').write(t); time.sleep(.2)
    return p
with ThreadPoolExecutor(3) as ex: paths=list(ex.map(get,[r for _,r in docs.iterrows()]))
out=[]
for (_,r),p in zip(docs.iterrows(),paths):
    tx=html.unescape(re.sub(r'<[^>]+>',' ',open(p).read())); tx=re.sub(r'\s+',' ',tx)
    key=r.center.split()[0]
    for m in re.finditer(r"(?i)dick.?s sporting goods|house of sport|dick.?s",tx):
        w=tx[max(0,m.start()-600):m.end()+600]
        if re.search(key,w,re.I):
            out.append(dict(center=r.center,form=r.form,date=r.file_date,id=r['id'],new=r.new,ctx=w)); break
o=pd.DataFrame(out); o.to_csv('data/M02_center_dick_ctx.csv',index=False)
print(len(docs),'docs;',len(o),'with center+Dick within 600ch')
print(o.groupby('center').agg(n=('id','count'),new=('new','sum')))
