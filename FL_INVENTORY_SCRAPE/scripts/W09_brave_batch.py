# Run many Brave queries, write TSV of (query, title, url, snippet)
import sys, time, urllib.parse, csv
from curl_cffi import requests
from bs4 import BeautifulSoup
qs=[l.strip() for l in open(sys.argv[1]) if l.strip()]
out=open(sys.argv[2],"a",newline=""); w=csv.writer(out,delimiter="\t")
s=requests.Session(impersonate="chrome")
for q in qs:
    for attempt in range(3):
        r=s.get("https://search.brave.com/search?q="+urllib.parse.quote(q),timeout=30)
        if r.status_code==200 and "snippet" in r.text: break
        time.sleep(15)
    soup=BeautifulSoup(r.text,"lxml"); n=0
    for d in soup.select("div.snippet"):
        a=d.select_one("a[href^=http]")
        if not a or "brave.com" in a["href"]: continue
        title=d.select_one(".title, .snippet-title"); desc=d.select_one(".snippet-description, .description, .generic-snippet")
        w.writerow([q,(title.get_text(" ",strip=True) if title else "")[:200],a["href"],(desc.get_text(" ",strip=True) if desc else d.get_text(" ",strip=True))[:600]]); n+=1
    out.flush(); print(r.status_code,n,q,file=sys.stderr)
    time.sleep(4)
