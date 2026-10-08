import requests,time,sys
H={"User-Agent":"Research palazzolojustin@gmail.com"}
def cdx(u,**kw):
    p={"url":u,"output":"json","collapse":"urlkey","limit":3000,"fl":"original,timestamp,statuscode"}; p.update(kw)
    for i in range(2):
        try:
            r=requests.get("https://web.archive.org/cdx/search/cdx",params=p,headers=H,timeout=50)
            return r.json() if r.text.strip() else []
        except Exception as e: err=e
    return str(err)[:80]
for u in ["jobs.dickssportinggoods.com/*","careers.dickssportinggoods.com/*","dickssportinggoods.jobs/*","dickssportinggoods.wd1.myworkdayjobs.com/*","dickssportinggoods.wd5.myworkdayjobs.com/*"]:
    j=cdx(u); 
    if isinstance(j,str): print(u,"ERR",j);continue
    rows=j[1:]; print(u,len(rows),flush=True)
    for r in rows[:4]: print("  ",r)
    print("  hos:",[r for r in rows if 'house' in r[0].lower()][:5],flush=True)
