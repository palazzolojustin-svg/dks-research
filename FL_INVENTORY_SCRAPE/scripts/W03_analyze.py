import json,csv,statistics as st,re,sys
rows=[json.loads(l) for l in open("raw/W03/snap_parsed.jsonl")]
rows=[r for r in rows if "pag" in r and r["pag"]]
BR=["Nike","Jordan","adidas","New Balance","On","ASICS","HOKA","Salomon","Puma","UGG","Vans","Converse","Under Armour","Champion"]
def norm(s): return re.sub(r'[^a-z]','',s.lower())
out=[]
for r in rows:
    f=r["facets"];m=f.get("miscellaneous",{})
    sale=m.get("Sale Product",m.get("Sale"))
    tot=r["pag"]["totalResults"]
    pr=r["prods"]
    d=[1-p["p"]/p["op"] for p in pr if p["op"] and p["p"] and p["p"]<p["op"]]
    vs=[v for p in pr for v in p["v"] if v[0]]
    vd=[1-v[1]/v[0] for v in vs if v[1] is not None and v[1]<v[0]]
    b={norm(k):v for k,v in f.get("brand",{}).items()}
    row=dict(target=r["target"],ts=r["ts"][:8],total=tot,sale_facet=sale,sale_share=round(sale/tot,3) if sale and tot else "",
      n_brands=len(b),p1_n=len(pr),p1_sale_share=round(len(d)/len(pr),3) if pr else "",p1_depth=round(st.mean(d),3) if d else "",
      p1_variant_sale_share=round(len(vd)/len(vs),3) if vs else "",
      p1_variant_depth=round(st.mean(vd),3) if vd else "")
    for k in BR: row["b_"+k]=b.get(norm(k),"")
    pf=f.get("price",{})
    row["price_150plus"]=next((v for k,v in pf.items() if "150" in k or "200" in k and "over" in k.lower()),"")
    out.append(row)
out.sort(key=lambda x:(x["target"],x["ts"]))
keys=list(out[0].keys())
for o in out:
    for k in o:
        if k not in keys: keys.append(k)
w=csv.DictWriter(open("data/W03_timeseries.csv","w",newline=""),fieldnames=keys);w.writeheader();w.writerows(out)
tg=sys.argv[1:]
for o in out:
    if any(t in o["target"] for t in tg):
        print(o["target"].replace("footlocker.com/category/","FL/").replace("champssports.com/category/","CH/"),o["ts"],o["total"],o["sale_facet"],o["sale_share"],o["p1_variant_depth"],"nb",o["n_brands"],"N",o["b_Nike"],"J",o["b_Jordan"],"NB",o["b_New Balance"],"On",o["b_On"],"Sal",o["b_Salomon"])
