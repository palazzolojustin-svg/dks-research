# Simple search-engine scraper (Bing / DuckDuckGo html) -> prints title|url|snippet
import sys, time, urllib.parse
from curl_cffi import requests
from bs4 import BeautifulSoup
eng=sys.argv[1]; q=sys.argv[2]; pages=int(sys.argv[3]) if len(sys.argv)>3 else 1
s=requests.Session(impersonate="chrome")
for p in range(pages):
    if eng=="bing":
        u="https://www.bing.com/search?q="+urllib.parse.quote(q)+f"&first={1+p*10}&count=10"
        r=s.get(u,timeout=30); soup=BeautifulSoup(r.text,"lxml")
        for li in soup.select("li.b_algo"):
            a=li.select_one("h2 a"); sn=li.select_one(".b_caption p, p")
            if a: print(a.get_text(" ",strip=True),"|",a.get("href"),"|",sn.get_text(" ",strip=True)[:300] if sn else "")
    else:
        r=s.post("https://html.duckduckgo.com/html/",data={"q":q,"s":str(p*30)},timeout=30); soup=BeautifulSoup(r.text,"lxml")
        for res in soup.select(".result"):
            a=res.select_one("a.result__a"); sn=res.select_one(".result__snippet")
            if a: print(a.get_text(" ",strip=True),"|",a.get("href"),"|",sn.get_text(" ",strip=True)[:300] if sn else "")
    time.sleep(2)
