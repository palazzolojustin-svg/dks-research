import requests,json
H={"User-Agent":"Research palazzolojustin@gmail.com"}
for u in ["jobs.dickssportinggoods.com*","dickssportinggoods.jobs*","careers.dickssportinggoods.com*","dickssportinggoods.wd5.myworkdayjobs.com*","*.dickssportinggoods.com/job/*","jobs.dickssportinggoods.com/job/*","jobs.dickssportinggoods.com/*house*"]:
    try:
        r=requests.get("https://web.archive.org/cdx/search/cdx",params={"url":u,"output":"json","limit":5,"filter":"statuscode:200","collapse":"urlkey"},headers=H,timeout=60)
        j=r.json() if r.text.strip() else []
        print(u,len(j)-1 if j else 0,j[1:3])
    except Exception as e: print(u,"ERR",e)
