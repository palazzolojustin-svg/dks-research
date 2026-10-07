# W12 fetcher: python3 W12_fetch.py name url [name url ...] -> raw/W12/<name>.txt (+ count of Foot Locker mentions)
import sys,re,time
from curl_cffi import requests
from bs4 import BeautifulSoup
out="/home/user/dks-research/FL_INVENTORY_SCRAPE/raw/W12/"
a=sys.argv[1:]
for k,u in zip(a[::2],a[1::2]):
    try:
        r=requests.get(u,impersonate="chrome",timeout=45)
        if u.lower().endswith(".pdf") or r.headers.get("content-type","").startswith("application/pdf"):
            open(out+k+".pdf","wb").write(r.content); print(k,r.status_code,"pdf",len(r.content)); continue
        s=BeautifulSoup(r.text,"lxml")
        for x in s(["script","style","nav","footer"]): x.decompose()
        t=s.get_text(" ",strip=True)
        open(out+k+".txt","w").write(u+"\n"+t)
        print(k,r.status_code,len(t),"FL:",len(re.findall(r"Foot ?Locker",t,re.I)))
    except Exception as e: print(k,"ERR",e)
    time.sleep(1.5)
