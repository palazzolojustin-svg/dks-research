import re,time,csv
from curl_cffi import requests as r
from bs4 import BeautifulSoup
rows={}
for p in range(1,16):
    u=f"https://www.dickssportinggoods.jobs/jobs/?&filter[brand]=House+of+Sport&mypage={p}"
    try: x=r.get(u,impersonate="chrome",timeout=40)
    except Exception as e: print(p,"ERR",e); continue
    s=BeautifulSoup(x.text,"lxml"); a=s.select("a[href*='/job/']"); 
    print(p,x.status_code,len(a),end="; ")
    for l in a:
        h=l.get("href"); t=l.get_text(" ",strip=True)
        m=re.search(r"/job/([^/]+)/([^/]+)/(\d+)",h)
        if not m: continue
        d=re.search(r"Date posted (\S+(?: \S+ ago)?)",t)
        loc=t.split(" Date posted")[0]
        rows[m.group(3)]=(m.group(2),m.group(1),d.group(1) if d else "",t[:200])
    time.sleep(1)
    if not a: break
w=csv.writer(open("data/J07_live_hos_postings_20261008.csv","w"));w.writerow(["id","citystate","slug","posted","text"])
for k,v in rows.items(): w.writerow([k,*v])
import collections
c=collections.Counter(v[0] for v in rows.values());print();print(len(rows))
for k,v in c.most_common(): print(k,v)
