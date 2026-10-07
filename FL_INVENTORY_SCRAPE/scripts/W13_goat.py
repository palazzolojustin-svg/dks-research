"""Look up GOAT (Algolia public search index) resale asks for FL/Champs calendar launches.
usage: python3 -I W13_goat.py in.csv out.csv"""
import requests, json, sys, time, re, statistics, pandas as pd
H={"x-algolia-application-id":"2FWOTDVM2O","x-algolia-api-key":"ac96de6fef0e02bb95d433d8d5c7038a","Content-Type":"application/json"}
URL="https://2fwotdvm2o-dsn.algolia.net/1/indexes/product_variants_v2/query"
S=requests.Session()
def q(query,n=200,filters=None):
    p="query="+requests.utils.quote(query)+f"&hitsPerPage={n}"
    if filters: p+="&filters="+requests.utils.quote(filters)
    for a in range(3):
        try:
            r=S.post(URL,headers=H,data=json.dumps({"params":p}),timeout=30); return r.json().get('hits',[])
        except Exception as e: time.sleep(3)
    return []
STOP=r"\b(grade school|pre school|toddler|in store only|men's|women's|mens|womens|retro og|- )\b"
def clean(name): 
    n=re.sub(r"(?i)\b(grade school|pre school|toddler|in store only|w|m)\b"," ",name); return re.sub(r"[^A-Za-z0-9 ]"," ",n)
def lookup(fid,name,launch):
    fid=str(fid).lower()
    hits=q(fid,50)
    cand=[h for h in hits if fid in (h.get('search_sku') or '') or (h.get('search_sku') or '').startswith(fid[:7])]
    how='sku'
    if not cand:
        hits=q(clean(name),200); how='name'
        ld=pd.Timestamp(launch.replace(' GMT+0000',''))
        cand=[]
        for h in hits:
            sk=h.get('search_sku') or ''
            if fid and (fid[1:] in sk or fid[:-1] in sk or (len(fid)>=7 and fid[-7:] in sk)): cand.append(h); how='name+sku'
        if not cand:
            for h in hits:
                rd=h.get('release_date')
                if rd:
                    try:
                        if abs((pd.Timestamp(rd[:10])-ld.normalize()).days)<=7: cand.append(h)
                    except Exception: pass
            how='name+date'
    if not cand: return None
    # group by template, take the template with most hits
    from collections import Counter
    t=Counter(h['product_template_id'] for h in cand).most_common(1)[0][0]
    th=[h for h in q(cand[0]['search_sku'] or '',200) if h['product_template_id']==t] or [h for h in cand if h['product_template_id']==t]
    retail=th[0].get('retail_price_cents_usd') or th[0].get('retail_price_cents')
    asks=[h['lowest_price_cents_usd'] for h in th if h.get('lowest_price_cents_usd') and h.get('has_stock')]
    under=[h for h in th if h.get('is_under_retail')]
    return dict(goat_name=th[0]['name'],goat_sku=th[0].get('sku'),goat_release=(th[0].get('release_date') or '')[:10],match=how,
        retail=retail/100 if retail else None,n_sizes=len(th),n_sizes_ask=len(asks),
        median_ask=statistics.median(asks)/100 if asks else None,min_ask=min(asks)/100 if asks else None,
        share_sizes_under_retail=round(sum(1 for a in asks if retail and a<retail)/len(asks),3) if asks and retail else None,
        template_under_retail=any(h.get('is_under_retail') for h in th))
if __name__=='__main__':
    d=pd.read_csv(sys.argv[1]); out=[]
    for i,r in d.iterrows():
        res=lookup(r['id'],r['name'],r['launch']) or {}
        out.append({**r.to_dict(),**res}); time.sleep(0.4)
        print(i,r['name'],res.get('goat_name'),res.get('retail'),res.get('median_ask'),flush=True)
    pd.DataFrame(out).to_csv(sys.argv[2],index=False)
