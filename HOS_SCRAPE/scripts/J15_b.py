from curl_cffi import requests as r
from bs4 import BeautifulSoup
import re,collections,csv
rows=[]
for p in range(1,25):
    u="https://www.dickssportinggoods.jobs/jobs/?&filter[brand]=House+of+Sport&mypage=%d"%p
    x=r.get(u,impersonate="chrome",timeout=30)
    s=BeautifulSoup(x.text,"lxml")
    n=0
    for a in s.select("a"):
        h=a.get("href","")
        if "/job/" in h:
            t=a.get_text(" ",strip=True); d=re.search(r"Date posted (\S+)",t)
            rows.append((p,t,d.group(1) if d else "",h)); n+=1
    if n==0: break
print(len(rows))
seen={}
for x in rows: seen[x[3]]=x
rows=list(seen.values()); print("uniq",len(rows))
with open("data/J15_hos_open_reqs.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow("page title posted href".split()); w.writerows(rows)
c=collections.Counter(); hourly=collections.Counter()
for p,t,d,h in rows:
    city=h.split("/")[-3]+"-"+h.split("/")[-2]
    c[t.split(" Date")[0].split(" Assistant")[0][:40]]+=0
    m=re.search(r"/job/([^/]+)/([^/]+)/",h); c2=(m.group(2)); c[c2]+=1
    if re.search(r"associate|lead|tech|climb",t,re.I): hourly[c2]+=1
print(sorted([(k,v) for k,v in c.items() if v],key=lambda z:-z[1]))
import pandas as pd
d=pd.DataFrame(rows,columns=["p","t","d","h"]); d["city"]=d.h.str.extract(r"/job/[^/]+/([^/]+)/")
d["role"]=d.h.str.extract(r"/job/([^/]+)/")
print(d.groupby("city").agg(n=("h","count"),first=("d","min"),last=("d","max")).sort_values("n",ascending=False).to_string())
print("hourly",hourly.most_common())
