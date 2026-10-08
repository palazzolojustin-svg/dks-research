import sys,json,csv,collections,datetime as dt,statistics as st
sys.path.insert(0,'/home/user/dks-research/FL_INVENTORY_SCRAPE/scripts')
import W01_fetch as F
R='/home/user/dks-research/FL_INVENTORY_SCRAPE/'
# 1) live top-level pages
pages=[]
for dom in ['footlocker.com','champssports.com','kidsfootlocker.com','footlocker.ca']:
    for path in ['/category/mens/shoes.html','/category/womens/shoes.html','/category/kids/shoes.html','/category/sale.html','/category/shoes.html','/category/mens.html']:
        t=F.get('https://www.%s%s'%(dom,path))
        if not t: print(dom,path,'FAIL');continue
        pg,fac,pr=F.parse(t)
        if not pg: print(dom,path,'noobj');continue
        misc={}
        for x in fac or []:
            if x['code'] in('miscellaneous','saleProduct','sale'): misc.update({v['name']:v['count'] for v in x['values']})
        tot=pg['totalResults']; sale=misc.get('Sale Product',misc.get('Sale'))
        pages.append(dict(dom=dom,path=path,date='20261008',total=tot,sale=sale,share=round(sale/tot,3) if sale and tot else '',misc=json.dumps(misc)[:150]))
        print(dom,path,tot,sale,misc.keys())
json.dump(pages,open(R+'raw/V1/live_pages.json','w'))
