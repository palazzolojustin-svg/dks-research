import re,time,csv,json,sys
from curl_cffi import requests as r
pat=re.compile(r'"name":"([^"]+)","originalPrice":\{"value":([\d.]+)[^}]*\},"price":\{"value":([\d.]+)[^}]*\}(?:,"reviewRatings":\{"reviews":(\d+))?',re.S)
def crawl(base,pages,tag):
    rows=[];seen=set()
    for p in range(pages):
        u=f"https://www.footlocker.com/category/{base}.html?currentPage={p}&query=:relevance"
        try:x=r.get(u,impersonate="chrome",timeout=30)
        except Exception as e: print(tag,p,'err');continue
        t=x.text
        if p==0: open(f'raw/W05/{tag}_p0.html','w').write(t)
        n=0
        for m in re.finditer(r'\{"badges":.*?"sku":"(\w+)"',t):
            blk=m.group(0);sku=m.group(1)
            if sku in seen: continue
            mm=pat.search(blk)
            if not mm: continue
            seen.add(sku);n+=1
            rows.append(dict(src=tag,page=p,sku=sku,name=mm.group(1),orig=float(mm.group(2)),price=float(mm.group(3)),reviews=mm.group(4) or ''))
        print(tag,p,n,len(rows),flush=True)
        time.sleep(1.2)
    return rows
allr=crawl("mens/shoes",48,"fl_mens_shoes")+crawl("sale/mens/shoes",7,"fl_sale_mens_shoes")
w=csv.DictWriter(open('raw/W05/fl_rows.csv','w'),fieldnames=allr[0].keys());w.writeheader();w.writerows(allr)
