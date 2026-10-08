import json,sys
from curl_cffi import requests as r
pats=["indeed.com/*house-of-sport*","indeed.com/q-dick*house*sport*","*ziprecruiter.com/*House-Of-Sport*","*simplyhired.com/*house-of-sport*","glassdoor.com/*house-of-sport*","glassdoor.com/Job/*house-of-sport*","linkedin.com/jobs/*house-of-sport*","linkedin.com/jobs/view/*house-of-sport*","*jobs.dickssportinggoods.com/*house-of-sport*","*talent.com/*house-of-sport*","*snagajob.com/*house*sport*","*lensa.com/*house-of-sport*","*jooble*house-of-sport*"]
for p in pats:
    try:
        x=r.get("https://web.archive.org/cdx/search/cdx",params={"url":p,"output":"json","limit":"300","fl":"timestamp,original,statuscode","filter":"statuscode:200"},timeout=60)
        j=x.json()
        print(p,x.status_code,len(j)-1 if j else 0)
        for row in j[1:8]: print("   ",row)
        json.dump(j,open("raw/J08/cdx_"+p.replace('*','S').replace('/','_')+".json","w"))
    except Exception as e: print(p,"ERR",str(e)[:80])
