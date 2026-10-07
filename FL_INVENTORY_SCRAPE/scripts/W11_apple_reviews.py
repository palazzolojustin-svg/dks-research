"""W11: Apple App Store customer-review RSS (max 10 pages x 50, newest first) -> raw/W11/apple_<id>.csv"""
import json, time, os, sys, requests
import pandas as pd
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'raw', 'W11')
APPS = {"FL":934030757,"Champs":994624624,"KFL":1375706708,"FinishLine":905940653,"JD":1477500619,"Hibbett":1325232713,"DKS":556653197}
for n,i in APPS.items():
    rows=[]
    for p in range(1,11):
        u=f"https://itunes.apple.com/us/rss/customerreviews/page={p}/id={i}/sortby=mostrecent/json"
        try: e=requests.get(u,timeout=30).json()['feed'].get('entry',[])
        except Exception as ex: print(n,p,ex); break
        if isinstance(e,dict): e=[e]
        if not e: break
        for x in e:
            if 'im:rating' not in x: continue
            rows.append({'date':x['updated']['label'],'rating':int(x['im:rating']['label']),'version':x.get('im:version',{}).get('label'),'title':x['title']['label'],'content':x['content']['label']})
        time.sleep(0.5)
    d=pd.DataFrame(rows); d.to_csv(os.path.join(RAW,f'apple_{n}.csv'),index=False)
    print(n,len(d),d['date'].min() if len(d) else None, d['date'].max() if len(d) else None, flush=True)
