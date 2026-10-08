import re,time,csv,collections
from curl_cffi import requests as r
from bs4 import BeautifulSoup
import pandas as pd
rows={}
def grab(u):
    x=r.get(u,impersonate="chrome",timeout=40)
    s=BeautifulSoup(x.text,"lxml");n=0
    for l in s.select("a[href*='/job/']"):
        h=l.get("href");t=l.get_text(" ",strip=True)
        m=re.search(r"/job/([^/]+)/([^/]+)/(\d+)",h)
        if not m: continue
        d=re.search(r"Date posted (\d\d/\d\d/\d{4}|30\+ days ago)",t)
        rows[m.group(3)]=(m.group(2),m.group(1),d.group(1) if d else "",t[:220]);n+=1
    return n
for p in range(1,17):
    n=grab(f"https://www.dickssportinggoods.jobs/jobs/brand/House-of-Sport/?page={p}");print(p,n,end="; ")
    if n==0:break
    time.sleep(1)
old=pd.read_csv("data/J07_live_hos_postings_20261008.csv",dtype=str)
for _,o in old.iterrows(): rows.setdefault(o.id,(o.citystate,o.slug,o.posted,o.text))
d=pd.DataFrame([(k,*v) for k,v in rows.items()],columns=["id","citystate","slug","posted","text"])
d.to_csv("data/J07_live_hos_postings_20261008.csv",index=False)
print(len(d),d.citystate.nunique())
print(d.citystate.value_counts().to_string())
