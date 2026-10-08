from curl_cffi import requests as r
import re
for u in ["https://www.dickssportinggoods.jobs/jobs/brand/House-of-Sport/","https://www.reveliolabs.com/companies/dick-s-sporting-goods/employees"]:
    try:
        x=r.get(u,impersonate="chrome",timeout=30); print(u,x.status_code,len(x.text)); open("raw/J15/"+u.split('/')[-2][:30]+".html","w").write(x.text)
    except Exception as e: print(u,e)
