import requests,time,sys,json
def cdx(params,tries=4):
    for i in range(tries):
        try:
            r=requests.get("https://web.archive.org/cdx/search/cdx",params=params,timeout=120)
            if r.status_code==200: return r.text
            print("st",r.status_code,file=sys.stderr)
        except Exception as e: print("err",str(e)[:80],file=sys.stderr)
        time.sleep(4*(i+1))
    return ""
if __name__=="__main__":
    for d in ["footlocker.com","champssports.com"]:
        for pat in [d+"/category/*",d+"/sale*",d+"/api/*"]:
            t=cdx({"url":pat,"output":"txt","from":"2024","to":"2026","filter":"statuscode:200","fl":"timestamp,original","collapse":"urlkey","limit":25})
            print("==",pat,len(t.splitlines()));print(t[:1800])
