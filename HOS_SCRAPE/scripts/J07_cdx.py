import requests,json
H={"User-Agent":"Research palazzolojustin@gmail.com"}
for q in ["jobs.dickssportinggoods.com/*house*","jobs.dickssportinggoods.com/*hiring*","jobs.dickssportinggoods.com/*event*","dickssportinggoods.com/*house-of-sport*hir*","jobs.dickssportinggoods.com/"]:
    try:
        r=requests.get("https://web.archive.org/cdx/search/cdx",params={"url":q,"output":"json","limit":40,"collapse":"urlkey","filter":"statuscode:200"},headers=H,timeout=60)
        d=r.json()
        print(q,len(d)-1)
        for x in d[1:25]: print(" ",x[1],x[2][:140])
    except Exception as e: print(q,"ERR",e)
