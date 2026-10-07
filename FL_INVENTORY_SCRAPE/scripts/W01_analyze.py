import json,csv,statistics as S,re,sys
R='/home/user/dks-research/FL_INVENTORY_SCRAPE/'
NEW={"Salomon","On","HOKA","New Balance","ASICS","UGG","Saucony","Mizuno","Brooks","Merrell","Birkenstock","Crocs","Timberland","Vans","Converse","Reebok","PUMA","Under Armour","K-Swiss","Lacoste","Havaianas"}
LEG=re.compile(r"Air Force 1|AF1|Dunk|Air Jordan|\bAJ ?\d|Air Max|Cortez|Blazer|Vomero|Pegasus|Retro|Jordan 1|Shox|TN|Metcon|Dri-FIT|Club Fleece|Tech Fleece",re.I)
def load(f,site):
    rows={}
    for l in open(R+'raw/W01/'+f):
        d=json.loads(l);p=d['p']
        key=(d['coll'],p['sku'])
        o=p['originalPrice']['value'];pr=p['price']['value']
        rows[key]=dict(site=site,collection=d['coll'],brand=d['brand'],sku=p['sku'],name=p['name'],list_price=o,price=pr,
          disc_pct=round(100*(o-pr)/o,1) if o else 0,on_sale=int(pr<o-0.005),saleflag=int(bool(p.get('isSaleProduct'))),
          reviews=(p.get('reviewRatings') or {}).get('reviews',0),is_new=int(bool(p.get('isNewProduct'))))
    return list(rows.values())
allr=[]
for f,s in (('products.jsonl','footlocker.com'),('champs_products.jsonl','champssports.com')):
    try: allr+=load(f,s)
    except FileNotFoundError: pass
w=csv.DictWriter(open(R+'data/W01_fl_champs_catalog_2026-10-07.csv','w'),fieldnames=list(allr[0]));w.writeheader();w.writerows(allr)
print(len(allr))
