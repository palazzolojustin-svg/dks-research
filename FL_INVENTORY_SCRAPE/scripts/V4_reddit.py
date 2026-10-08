import requests,time,pandas as pd
from concurrent.futures import ThreadPoolExecutor
A='https://arctic-shift.photon-reddit.com/api'
def get(path,p):
    for i in range(6):
        try:
            j=requests.get(A+path,params=p,timeout=90).json()
            if j.get('error'): raise RuntimeError(j['error'])
            return j['data']
        except Exception: time.sleep(3*(i+1))
    return None
starts=pd.date_range('2024-01-01','2026-11-01',freq='3MS')
subs=['footlocker','Sneakers','Sneakerheads','frugalmalefashion']
jobs=[]
for s in subs:
  for kind,fld in (('posts','title'),('comments','body')):
    for term in ('"foot locker"','champs','ALL'):
      if term=='ALL' and s!='footlocker': continue
      for a,b in zip(starts[:-1],starts[1:]): jobs.append((s,kind,fld,term,a,b))
def run(j):
    s,kind,fld,term,a,b=j
    p=dict(subreddit=s,aggregate='created_utc',frequency='month',after=a.strftime('%Y-%m-%d'),before=b.strftime('%Y-%m-%d'))
    if term!='ALL': p[fld]=term
    d=get(f'/{kind}/search/aggregate',p)
    return [(s,kind,term,x['created_utc'][:7],int(x['count'])) for x in d] if d is not None else [(s,kind,term,a.strftime('%Y-%m')+'?FAIL',-1)]
with ThreadPoolExecutor(4) as ex: res=[r for l in ex.map(run,jobs) for r in l]
pd.DataFrame(res,columns=['sub','kind','term','month','n']).to_csv('raw/V4/agg.csv',index=False)
print(len(res),sum(1 for r in res if r[4]<0))
