import requests, json, time, sys
base="https://api.nike.com/product_feed/threads/v3/"
params="?count=50&anchor={a}&filter=marketplace%28US%29&filter=language%28en%29&filter=channelId%28010794e5-35fe-4e32-aaff-cd2c74f89d61%29&filter=exclusiveAccess%28true%2Cfalse%29"
rows=[]; a=0
s=requests.Session(); s.headers['User-Agent']='Mozilla/5.0'
while a<2000:
    r=s.get(base+params.format(a=a),timeout=60); j=r.json()
    objs=j.get('objects',[])
    if not objs: break
    for o in objs:
        for pi in o.get('productInfo',[]) or []:
            mp=pi.get('merchProduct',{}); li=pi.get('launchView',{}) or {}; pr=pi.get('merchPrice',{})
            ci=pi.get('productContent',{})
            rows.append(dict(threadStart=o.get('publishedContent',{}).get('properties',{}).get('custom',{}).get('restricted') ,
              style=mp.get('styleColor'), title=ci.get('fullTitle') or ci.get('title'), brand=(mp.get('brand') or ''),
              launch=li.get('startEntryDate') or mp.get('commerceStartDate'), method=li.get('method'),
              price=pr.get('fullPrice'), status=mp.get('status'), exclusiveAccess=mp.get('exclusiveAccess'),
              hardLaunch=mp.get('hardLaunch'), pubType=mp.get('publishType'), commerceStart=mp.get('commerceStartDate')))
    a+=50; time.sleep(1)
json.dump(rows,open(sys.argv[1],'w'))
print(len(rows))
