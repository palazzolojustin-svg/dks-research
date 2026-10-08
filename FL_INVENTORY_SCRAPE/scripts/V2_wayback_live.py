import requests, time, json
def cdx(frm,to,limit=5000):
    for t in range(4):
        try:
            r=requests.get("https://web.archive.org/cdx/search/cdx",params={"url":"dickssportinggoods.com/f/*","output":"json","from":frm,"to":to,"filter":"statuscode:200","limit":limit},timeout=90)
            if r.status_code==200: return json.loads(r.text) if r.text.strip() else []
            print("wb",frm,r.status_code); 
        except Exception as e: print("wb err",str(e)[:60])
        time.sleep(6)
    return None
for frm,to in [("20250801","20251231"),("20260801","20261008")]:
    d=cdx(frm,to); print(frm,None if d is None else len(d)-1 if d else 0)
    if d: json.dump(d,open(f"raw/V2/wb_{frm}.json","w"))
# live
try:
    from curl_cffi import requests as cr
    for u in ["https://www.dickssportinggoods.com/f/mens-clothing","https://www.dickssportinggoods.com/f/nike-shoes"]:
        for t in range(2):
            r=cr.get(u,impersonate="chrome",timeout=40); print("live",u[-20:],r.status_code,len(r.text),"dcsg-ngx-plp" in r.text); time.sleep(3)
except Exception as e: print("live err",str(e)[:100])
