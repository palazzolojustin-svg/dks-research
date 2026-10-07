# Fetch public LinkedIn post/profile pages, extract post text (og:description / commentary)
import sys, time, re, json, hashlib, os
from curl_cffi import requests
from bs4 import BeautifulSoup
s=requests.Session(impersonate="chrome")
for u in sys.argv[1:]:
    try:
        r=s.get(u,timeout=30)
    except Exception as e:
        print("ERR",u,e); continue
    fn="raw/W09/li_"+hashlib.md5(u.encode()).hexdigest()[:10]+".html"
    open(fn,"w").write(r.text)
    soup=BeautifulSoup(r.text,"lxml")
    txt=[]
    for sel in ['[data-test-id="main-feed-activity-card__commentary"]','.attributed-text-segment-list__content','p.attributed-text-segment-list__content']:
        for e in soup.select(sel): txt.append(e.get_text(" ",strip=True))
    og=soup.find("meta",property="og:description")
    date=soup.select_one("time")
    print("=====",r.status_code,u,fn)
    print("TIME:", date.get_text(strip=True) if date else "")
    print("OG:", og["content"] if og else "")
    print("TXT:", " || ".join(dict.fromkeys(txt))[:3000])
    time.sleep(2)
