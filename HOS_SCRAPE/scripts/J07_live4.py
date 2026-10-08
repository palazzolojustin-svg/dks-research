import re,time,urllib.parse
from curl_cffi import requests as r
from bs4 import BeautifulSoup
import pandas as pd
d=pd.read_csv("data/J07_live_hos_postings_20261008.csv",dtype=str)
rows={o.id:(o.citystate,o.slug,o.posted,o.text) for _,o in d.iterrows()}
n0=len(rows)
for loc in ["Sacramento, CA","San Diego, CA","Phoenix, AZ","Denver, CO","Raleigh, NC","Detroit, MI","Chicago, IL","Houston, TX","Atlanta, GA","Boston, MA","Orlando, FL","Seattle, WA","Las Vegas, NV","Minneapolis, MN","Nashville, TN","Philadelphia, PA"]:
    new=0
    for p in range(1,15):
        u="https://www.dickssportinggoods.jobs/jobs/?location=%s&filter[brand]=House+of+Sport&page=%d"%(urllib.parse.quote_plus(loc),p)
        try:x=r.get(u,impersonate="chrome",timeout=40)
        except Exception as e: break
        s=BeautifulSoup(x.text,"lxml");a=s.select("a[href*='/job/']")
        if not a:break
        for l in a:
            m=re.search(r"/job/([^/]+)/([^/]+)/(\d+)",l.get("href"));t=l.get_text(" ",strip=True)
            if not m:continue
            dd=re.search(r"Date posted (\d\d/\d\d/\d{4}|30\+ days ago)",t)
            if m.group(3) not in rows:new+=1
            rows[m.group(3)]=(m.group(2),m.group(1),dd.group(1) if dd else "",t[:220])
    print(loc,"new",new,"total",len(rows),flush=True)
    if new==0 and loc!="Sacramento, CA": pass
df=pd.DataFrame([(k,*v) for k,v in rows.items()],columns=["id","citystate","slug","posted","text"])
df.to_csv("data/J07_live_hos_postings_20261008.csv",index=False)
print(df.citystate.nunique())
