import re,json,sys,time,urllib.parse
from curl_cffi import requests as r
def get(url):
    for _ in range(3):
        try:
            x=r.get(url,impersonate="chrome",timeout=45)
            if x.status_code==200: return x.text
        except Exception as e: pass
        time.sleep(2)
    return None
def brk(t,key):
    i=t.find('"'+key+'":')
    if i<0:return None
    s=i+len(key)+3
    o=t[s]; c=']' if o=='[' else '}'
    d=0
    for k in range(s,len(t)):
        if t[k]==o:d+=1
        elif t[k]==c:
            d-=1
            if d==0:return json.loads(t[s:k+1])
def parse(t):
    pg=re.search(r'"pagination":(\{[^}]*\})',t)
    fac=brk(t,'facets')
    prods=brk(t,'products')
    return (json.loads(pg.group(1)) if pg else None),fac,prods
if __name__=="__main__":
    for u in sys.argv[1:]:
        t=get(u)
        if not t: print(u,"FAIL");continue
        pg,f,p=parse(t)
        print(u,len(t),pg and pg['totalResults'],len(p or []))
