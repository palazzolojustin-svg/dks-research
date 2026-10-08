import sys,json,csv,time,urllib.parse,re
sys.path.insert(0,'/home/user/dks-research/FL_INVENTORY_SCRAPE/scripts')
import W01_fetch as F
SITE=sys.argv[1] if len(sys.argv)>1 else "footlocker"
BASE="https://www.footlocker.com/category/mens/shoes.html?query="
COLL={"men-s-shoes":"Men Shoes","women-s-shoes":"Women Shoes","kids-all-shoes":"Kids Shoes","men-s-clothing":"Men Apparel","women-s-clothing":"Women Apparel","kids-all-clothing":"Kids Apparel"}
CAL=sys.argv[2] if len(sys.argv)>2 else None
def q(parts): return BASE+urllib.parse.quote(":relevance"+"".join(":%s:%s"%(k,v) for k,v in parts),safe='')
def run(parts):
    t=F.get(q(parts)); time.sleep(0.6)
    if not t: return None,None,None
    return F.parse(t)
out=open('/home/user/dks-research/FL_INVENTORY_SCRAPE/raw/V1/census_products.jsonl','w')
rows=[]
for cid,cname in COLL.items():
    pg,fac,pr=run([("collection_id",cid)])
    brands=[(v['name'],v['count']) for x in fac for v in x['values'] if x['code']=='brand']
    print(cname,pg['totalResults'],len(brands),flush=True)
    for b,n in brands:
        res={}
        for lab,extra in (("all",[]),("sale",[("saleProduct","True")])):
            p,f,pr=run([("collection_id",cid),("brand",b)]+extra)
            if not p: res[lab]=(None,[]);continue
            tot=p['totalResults']; prods=pr or []
            if tot>len(prods) and f:   # slice by style to widen sample
                for x in f:
                    if x['code']=='style':
                        for v in x['values']:
                            if v['count']==0:continue
                            p2,f2,pr2=run([("collection_id",cid),("brand",b)]+extra+[("style",v['name'])])
                            if pr2:
                                seen={z['sku'] for z in prods}
                                prods+= [z for z in pr2 if z['sku'] not in seen]
            res[lab]=(tot,prods)
            for z in prods:
                out.write(json.dumps({"coll":cname,"brand":b,"slice":lab,"p":z})+"\n")
        rows.append((cname,b,n,res['all'][0],res['sale'][0],len(res['all'][1]),len(res['sale'][1])))
        print(cname,b,rows[-1][2:],flush=True)
w=csv.writer(open('/home/user/dks-research/FL_INVENTORY_SCRAPE/raw/V1/census_brand_counts.csv','w'))
w.writerow("collection brand facet_count total sale_total n_all_sampled n_sale_sampled".split()); w.writerows(rows)
print("DONE")
