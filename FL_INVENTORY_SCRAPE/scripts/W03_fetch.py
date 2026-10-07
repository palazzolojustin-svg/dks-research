import json,re,gzip,os,sys,time,csv,requests
d=json.JSONDecoder()
snaps=json.load(open("raw/W03/snaps.json"))
rows=[];D="raw/W03/html";os.makedirs(D,exist_ok=True)
def get(ts,u):
    fn=f"{D}/{ts}_{re.sub(r'[^a-z0-9]','_',u.lower())}.gz"
    if os.path.exists(fn): return gzip.open(fn,"rt").read()
    for i in range(3):
        try:
            r=requests.get(f"https://web.archive.org/web/{ts}id_/https://{u}",timeout=90)
            if r.status_code==200:
                gzip.open(fn,"wt").write(r.text); return r.text
            if r.status_code in(404,): return ""
        except Exception as e: pass
        time.sleep(3*(i+1))
    return ""
def jat(t,key):
    i=t.find(key)
    if i<0: return None
    try: return d.raw_decode(t[i+len(key):])[0]
    except Exception: return None
def parse(t):
    o={}
    m=re.search(r'"pagination":\{[^}]*"totalResults":(\d+)',t)
    o["total"]=int(m.group(1)) if m else None
    f=jat(t,'"facets":') or []
    for x in f:
        vals=x.get("values") or [v for n in x.get("nodes",[]) for v in (n.get("values") or [])]
        if x["name"]=="Brand": o["brands"]={v["name"]:v["count"] for v in vals}
        if x["name"]=="Miscellaneous":
            for v in vals: o["misc_"+v["name"]]=v["count"]
        if x["name"]=="Price": o["price"]={v["name"]:v["count"] for v in vals}
    p=jat(t,'"products":[{"badges"') if False else None
    j=t.find('"products":[{"badges"')
    if j>=0:
        try: p=d.raw_decode(t[j+11:])[0]
        except Exception: p=None
    if p:
        n=len(p);s=0;dd=[]
        for x in p:
            a=x.get("originalPrice",{}).get("value");b=x.get("price",{}).get("value")
            if a and b and b<a: s+=1;dd.append(1-b/a)
        o.update(p_n=n,p_sale=s,p_depth=round(sum(dd)/len(dd),4) if dd else 0)
    return o
if __name__=="__main__":
    out=[]
    for u,tss in snaps.items():
        for ts in tss:
            t=get(ts,u)
            o=parse(t) if t else {}
            o.update(url=u,ts=ts,bytes=len(t))
            out.append(o);print(u.split("/",1)[1],ts,o.get("total"),o.get("misc_Sale Product"),o.get("p_n"),flush=True)
            time.sleep(0.5)
    json.dump(out,open("raw/W03/parsed.json","w"))
