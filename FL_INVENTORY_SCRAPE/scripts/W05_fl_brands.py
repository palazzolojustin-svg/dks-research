import re,time,csv,json,urllib.parse as up
from curl_cffi import requests as r
def facet(t,name):
    i=t.find('{"name":"%s","multiSelect":true,"values":['%name)
    seg=t[i:i+40000]
    return {m.group(1):int(m.group(2)) for m in re.finditer(r'\{"name":"([^"]+)","count":(\d+),"selected"',seg)}
tot=facet(open('raw/W05/fl.html').read(),'Brand'); sal=facet(open('raw/W05/fl_sale.html').read(),'Brand')
print('TOTAL',tot);print('SALE',sal)
json.dump({'tot':tot,'sale':sal},open('raw/W05/fl_brand_facets.json','w'))
pat=re.compile(r'"name":"([^"]+)","originalPrice":\{"value":([\d.]+)[^}]*\},"price":\{"value":([\d.]+)[^}]*\}(?:,"reviewRatings":\{"reviews":(\d+))?')
rows=[]
for b in ["Nike","Jordan","adidas","New Balance","ASICS","HOKA","On","Salomon","Puma","Under Armour","Converse","Vans","Crocs","UGG","Timberland","Reebok","Saucony","Brooks","Skechers"]:
  for sale in (0,1):
    q=":relevance:collection_id:%s:brand:%s"%("sale" if sale else "men-s-shoes",b)
    if sale: q+=":gender:Men's"
    t=r.get("https://www.footlocker.com/search?query="+up.quote(q),impersonate="chrome",timeout=30).text
    n=0
    for blk in re.finditer(r'\{"badges":.*?"sku":"(\w+)"',t):
        mm=pat.search(blk.group(0))
        if mm: rows.append(dict(brand=b,slice='sale' if sale else 'all',sku=blk.group(1),name=mm.group(1),orig=float(mm.group(2)),price=float(mm.group(3)),reviews=mm.group(4) or ''));n+=1
    print(b,sale,n,re.findall(r'"totalResults":\d+',t)[:1],flush=True);time.sleep(1)
w=csv.DictWriter(open('raw/W05/fl_brand_rows.csv','w'),fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
