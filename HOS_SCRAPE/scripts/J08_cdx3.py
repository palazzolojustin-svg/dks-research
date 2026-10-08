import time
from curl_cffi import requests as r
doms=["indeed.com","ziprecruiter.com","simplyhired.com","glassdoor.com","linkedin.com","talent.com","snagajob.com","lensa.com","jooble.org","adzuna.com","jobs.dickssportinggoods.com","dickssportinggoods.jobs","careers.dickssportinggoods.com","salary.com","joblist.com","learn4good.com","jobrapido.com","monster.com","careerbuilder.com","workopolis.com"]
for d in doms:
    time.sleep(1.5)
    try:
        x=r.get("https://web.archive.org/cdx/search/cdx",params={"url":d,"matchType":"domain","fl":"timestamp,original,statuscode","filter":["original:.*[Hh]ouse.?[Oo]f.?[Ss]port.*"],"collapse":"timestamp:6","limit":"500"},timeout=180)
        L=x.text.strip().splitlines(); print(d,x.status_code,len(L))
        open(f"raw/J08/cdx3_{d}.txt","w").write(x.text)
        for l in L[:6]: print("   ",l[:170])
    except Exception as e: print(d,"ERR",str(e)[:70])
