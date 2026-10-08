import re,sys
from curl_cffi import requests as r
tests={
"indeed":"https://www.indeed.com/jobs?q=%22house+of+sport%22+dick%27s&l=",
"ziprecruiter":"https://www.ziprecruiter.com/jobs-search?search=dick%27s+house+of+sport",
"simplyhired":"https://www.simplyhired.com/search?q=%22house+of+sport%22",
"glassdoor":"https://www.glassdoor.com/Job/dick-s-sporting-goods-house-of-sport-jobs-SRCH_KE0,36.htm",
"linkedin_guest":"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=%22house%20of%20sport%22&f_C=&start=0",
"jobs_site":"https://www.dickssportinggoods.jobs/jobs/?q=house+of+sport",
}
for k,u in tests.items():
    try:
        x=r.get(u,impersonate="chrome",timeout=30)
        t=x.text
        print(k,x.status_code,len(t),len(re.findall(r'(?i)house of sport',t)))
        open(f"HOS_SCRAPE/raw/J08/{k}.html","w").write(t)
    except Exception as e: print(k,"ERR",e)
