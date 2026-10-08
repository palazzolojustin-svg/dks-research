import requests,time
H={"User-Agent":"Research palazzolojustin@gmail.com"}
def cdx(u,**kw):
    p={"url":u,"output":"json","filter":"statuscode:200","collapse":"urlkey"}; p.update(kw)
    for i in range(3):
        try:
            r=requests.get("https://web.archive.org/cdx/search/cdx",params=p,headers=H,timeout=90)
            return r.json() if r.text.strip() else []
        except Exception as e: time.sleep(3)
    return None
for u in ["jobs.dickssportinggoods.com","jobs.dickssportinggoods.com/*","dickssportinggoods.jobs/*","www.dickssportinggoods.jobs/*","careers.dickssportinggoods.com/*","dickssportinggoods.com/careers*","dickssportinggoods.com/s/careers*","*.myworkdayjobs.com/*dicks*"]:
    j=cdx(u,limit=2000,fl="original,timestamp",matchType="prefix" if u.endswith("*") is False else "exact")
    if j is None: print(u,"fail");continue
    rows=j[1:]
    print(u,len(rows)); 
    hos=[r for r in rows if any(k in r[0].lower() for k in ["house","hos","sport"])]
    print(" hos-ish",len(hos),hos[:5]); print(" sample",rows[:3])
