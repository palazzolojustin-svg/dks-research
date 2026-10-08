import sys,json
from curl_cffi import requests as r
u="https://www.dickssportinggoods.jobs/jobs/brand/House-of-Sport/"
x=r.get(u,impersonate="chrome",timeout=40)
print(x.status_code,len(x.text)); open("raw/J07/live_brand.html","w").write(x.text)
c=r.get("https://web.archive.org/cdx/search/cdx",params={"url":"dickssportinggoods.jobs/jobs/brand/House-of-Sport*","output":"json","limit":60,"collapse":"timestamp:6","filter":"statuscode:200"},timeout=60).json()
print(len(c)-1)
for z in c[1:60]: print(z[1],z[2])
