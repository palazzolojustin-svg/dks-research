# Brave search scraper: python3 W09_brave.py "<query>" [offset_pages]
import sys, time, urllib.parse, re
from curl_cffi import requests
from bs4 import BeautifulSoup
q=sys.argv[1]; pages=int(sys.argv[2]) if len(sys.argv)>2 else 1
s=requests.Session(impersonate="chrome")
seen=set()
for p in range(pages):
    u="https://search.brave.com/search?q="+urllib.parse.quote(q)+(f"&offset={p}" if p else "")
    r=s.get(u,timeout=30)
    soup=BeautifulSoup(r.text,"lxml")
    for d in soup.select("div.snippet"):
        a=d.select_one("a[href^=http]")
        if not a: continue
        href=a["href"]
        if href in seen or "brave.com" in href: continue
        seen.add(href)
        title=d.select_one(".title, .snippet-title")
        desc=d.select_one(".snippet-description, .description, .generic-snippet")
        print((title.get_text(" ",strip=True) if title else "")[:150],"|",href,"|",(desc.get_text(" ",strip=True) if desc else d.get_text(" ",strip=True))[:400])
    time.sleep(3)
