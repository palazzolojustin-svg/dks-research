import sys,json,time
sys.path.insert(0,'scripts')
from W03_cdx import cdx
urls=[]
for d in ["www.footlocker.com","www.champssports.com"]:
    for p in ["category/mens/shoes.html","category/womens/shoes.html","category/sale.html","category/mens/sale.html","category/new-arrivals.html","category/mens/shoes/sale.html","category/shoes.html","category/mens.html","category/kids/shoes.html","category/mens/clothing.html"]:
        urls.append(f"{d}/{p}")
out={}
for u in urls:
    t=cdx({"url":u,"output":"txt","from":"2024","to":"2026","filter":"statuscode:200","fl":"timestamp","collapse":"timestamp:6"},tries=3)
    ts=t.split()
    out[u]=ts
    print(u,len(ts),ts[:1],ts[-1:],flush=True)
    time.sleep(1)
json.dump(out,open("raw/W03/snaps.json","w"))
