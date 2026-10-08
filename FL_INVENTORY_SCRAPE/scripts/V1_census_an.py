import json,csv,collections,statistics as st
R='/home/user/dks-research/FL_INVENTORY_SCRAPE/raw/V1/'
def load(f):
    rows={}
    for l in open(R+f):
        d=json.loads(l);p=d['p']
        key=(d['coll'],p['sku'])
        dates=[];vs=[]
        for v in p.get('variantOptions',[]) or []:
            nd=v.get('newArrivalDate') or (v.get('flagsAndRestrictions') or {}).get('newArrivalDate')
            vp=v.get('price') or {}
            if nd and nd[:4]>'1950': dates.append(nd[:10])
        o=p['originalPrice']['value'];pr=p['price']['value']
        rows[key]=dict(coll=d['coll'],brand=d['brand'],sku=p['sku'],o=o,pr=pr,sale=pr<o-0.005,first=min(dates) if dates else None,last=max(dates) if dates else None,isnew=bool((p.get('badges') or {}).get('isNewProduct')),reviews=(p.get('reviewRatings') or {}).get('reviews',0))
    return list(rows.values())
for f,name in (('census_products.jsonl','FL'),('census_champs_champs_products.jsonl','CH')):
    rs=load(f); print(name,'products',len(rs),'with date',sum(1 for r in rs if r['first']))
    for coll in sorted({r['coll'] for r in rs})+['ALL SHOES']:
        sub=[r for r in rs if (r['coll']==coll or (coll=='ALL SHOES' and 'Shoes' in r['coll'])) and r['first']]
        if not sub: continue
        n=len(sub)
        def share(cut,key='first'): return sum(1 for r in sub if r[key]>cut)/n
        post1=[r for r in sub if r['first']>'2025-09-08']; pre1=[r for r in sub if r['first']<='2025-09-08']
        post2=[r for r in sub if r['first']>'2026-07-01']; pre2=[r for r in sub if r['first']<='2026-07-01']
        sr=lambda L:(round(sum(r['sale'] for r in L)/len(L),3) if L else None)
        # uses last (latest variant) as well
        print(f"{name} {coll}: n={n} first>2025-09-08 {share('2025-09-08'):.3f} | >2026-07-01 {share('2026-07-01'):.3f} | onsale new(>9/8/25) {sr(post1)} (n={len(post1)}) old {sr(pre1)} (n={len(pre1)}) | new(>7/1/26) {sr(post2)} (n={len(post2)}) older {sr(pre2)} | median first {sorted(r['first'] for r in sub)[n//2]}")
    # sale slice sampled bias: note
