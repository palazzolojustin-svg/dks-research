import re,json,time,csv
from curl_cffi import requests as r
out=[]
def get(u):
    try:
        x=r.get(u,impersonate="chrome",timeout=30);time.sleep(1);return x.status_code,x.text
    except Exception as e:return 0,''
NIKE={"nike_mens_shoes":"https://www.nike.com/w/mens-shoes-nik1zy7ok","nike_mens_sale":"https://www.nike.com/w/mens-sale-shoes-3yaepznik1zy7ok","nike_mens_running":"https://www.nike.com/w/mens-running-shoes-37v7jznik1zy7ok","nike_mens_lifestyle":"https://www.nike.com/w/mens-lifestyle-shoes-13jrmznik1zy7ok","nike_jordan_men":"https://www.nike.com/w/mens-jordan-shoes-37eefznik1zy7ok","nike_mens_basketball":"https://www.nike.com/w/mens-basketball-shoes-3glsmznik1zy7ok","nike_new":"https://www.nike.com/w/new-mens-shoes-3n82yznik1zy7ok","nike_airmax":"https://www.nike.com/w/mens-air-max-shoes-a6d8hznik1zy7ok"}
for k,u in NIKE.items():
    c,t=get(u);m=re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>',t,re.S)
    if not m:print(k,c,'none');continue
    d=json.loads(m.group(1));n=0;ss=m.group(1);tr=re.findall(r'"totalResources":\s*(\d+)',ss)[:1]
    def walk(o):
        if isinstance(o,dict):
            if 'productCode' in o and 'prices' in o: yield o
            for v in o.values(): yield from walk(v)
        elif isinstance(o,list):
            for v in o: yield from walk(v)
    seen=set()
    for g in walk(d):
        if g['productCode'] in seen: continue
        seen.add(g['productCode']);pr=g['prices']
        out.append(dict(retailer='nike.com',slice=k,code=g['productCode'],name=g['copy']['title'],price=pr['currentPrice'],orig=pr['initialPrice']));n+=1
    print(k,c,n,tr)
Z={"zap_run":"https://www.zappos.com/men-running-shoes/CK_XAVcBwAECAQM.zso","zap_sneak":"https://www.zappos.com/men-sneakers-athletic-shoes/CK_XARC81wHAAQLiAgMBAhg.zso"}
for k,u in Z.items():
    c,t=get(u)
    n=0
    for g in re.finditer(r'"originalPrice":"\$([\d,.]+)","color":"[^"]*","colorId":\d+,[^{}]*?"productName":"([^"]+)"[^{}]*?"price":"\$([\d,.]+)"[^{}]*?"onSale":"(\w+)"[^{}]*?"brandName":"([^"]+)"',t):
        out.append(dict(retailer='zappos',slice=k,code=g.group(5),name=g.group(2),price=float(g.group(3).replace(',','')),orig=float(g.group(1).replace(',','')))) ;n+=1
    print(k,c,n,re.findall(r'"totalProductCount":(\d+)',t)[:1])
HB={"hib_run":"https://www.hibbett.com/mens-shoes/running-shoes/","hib_all":"https://www.hibbett.com/mens-shoes/","hib_nike":"https://www.hibbett.com/mens-shoes/?prefn1=brand&prefv1=Nike","hib_jordan":"https://www.hibbett.com/jordan/mens-shoes/"}
for k,u in HB.items():
    c,t=get(u);n=0
    for g in re.finditer(r'\{"id":"(\w+)","name":"([^"]+)","parentID":"\w+","brand":"([^"]*)","category":"[^"]*","price":([\d.]+)[^}]*?"discount":([\d.]+)',t):
        pr=float(g.group(4));d=float(g.group(5));out.append(dict(retailer='hibbett',slice=k,code=g.group(3),name=g.group(2),price=pr,orig=pr+d if d<pr else pr/(1-d/100) if d<100 else pr));n+=1
    print(k,c,n,re.findall(r'(\d[\d,]*) (?:Results|results|Products|items)',t)[:2])
w=csv.DictWriter(open('raw/W05/others_rows.csv','w'),fieldnames=['retailer','slice','code','name','price','orig']);w.writeheader();w.writerows(out)
