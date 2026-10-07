import requests, re, sys, html
from bs4 import BeautifulSoup
H={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36","Accept-Language":"en-US,en;q=0.9"}
urls=sys.argv[1:]
for u in urls:
    try:
        r=requests.get(u,headers=H,timeout=40)
        s=BeautifulSoup(r.text,"html.parser")
        for t in s(["script","style","nav","footer","header"]): t.decompose()
        txt=re.sub(r"\s+"," ",s.get_text(" "))
        print("=====",u,r.status_code,len(txt))
        kw=re.compile(r"(CALIA|Calia|VRST|DSG|Maxfli|MaxFli|Walter Hagen|Top Flite|Top-Flite|vertical|private label|private-label|owned brand|in-house|exclusive brand|Dick's|DICK'S|Dick’s)")
        for m in kw.finditer(txt):
            pass
        # print sentences containing keywords
        sents=re.split(r"(?<=[.!?])\s+",txt)
        seen=set()
        for x in sents:
            if kw.search(x) and x not in seen and len(x)<700:
                seen.add(x); print("-",x)
    except Exception as e: print("ERR",u,e)
