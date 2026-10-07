import json,time,csv,re
from curl_cffi import requests as r
rows=[];tot=None
for a in range(0,480,24):
    u=("https://api.nike.com/cic/browse/v2?queryid=products&anonymousId=0&country=us&endpoint=%2Fproduct_feed%2Frollup_threads%2Fv2%3Ffilter%3Dmarketplace(US)%26filter%3Dlanguage(en)%26filter%3DemployeePrice(true)%26filter%3DattributeIds(0f64ecc7-d624-4e91-b171-b83a03dd8550%2C16633190-45e5-4830-a068-232ac7aea82c)%26anchor%3D"+str(a)+"%26consumerChannelId%3Dd9a5bc42-4b9c-4976-858a-f159cf99c647%26count%3D24")
    x=r.get(u,impersonate="chrome",timeout=30,headers={"nike-api-caller-id":"nike:dotcom:browse:wall.client:2.0"})
    if x.status_code!=200: print(a,x.status_code,x.text[:100]);break
    j=x.json();tot=j.get('data',{}).get('products',{}).get('pages',{}).get('totalResources',tot)
    for g in j['data']['products']['products']:
        p=g['prices'];rows.append(dict(code=g['productCode'],title=g['copy']['title'],cur=p['currentPrice'],init=p['initialPrice']))
    time.sleep(1)
print(tot,len(rows))
if rows:
    w=csv.DictWriter(open('raw/W05/nike_rows.csv','w'),fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
