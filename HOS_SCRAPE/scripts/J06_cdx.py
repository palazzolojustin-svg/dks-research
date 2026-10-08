import requests,time,sys,os
H={'User-Agent':'Mozilla/5.0 research'}
def get(u,tries=8,to=120):
    for a in range(tries):
        try:
            r=requests.get(u,headers=H,timeout=to)
            if r.status_code==200: return r.text
        except Exception as e: pass
        time.sleep(6*(a+1))
    return None
if __name__=='__main__':
    t=get("https://web.archive.org/cdx/search/cdx?url=dickssportinggoods.jobs/jobs-sitemap.xml&matchType=prefix&output=txt&fl=timestamp,original,length,digest&filter=statuscode:200&from=2023")
    open('raw/J06/cdx_sitemap.txt','w').write(t or '')
    print(t)
