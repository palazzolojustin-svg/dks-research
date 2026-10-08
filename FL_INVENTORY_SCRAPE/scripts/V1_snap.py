"""Fetch all Wayback captures (1 per day) of key category URLs across 4 domains; parse; append to raw/V1/snaps.jsonl"""
import sys,json,re,os,urllib.parse,concurrent.futures as cf
sys.path.insert(0,'/home/user/dks-research/FL_INVENTORY_SCRAPE/scripts')
import W03_wb as w, W03_parse as P
D='/home/user/dks-research/FL_INVENTORY_SCRAPE/raw/V1'
OUT=D+'/snaps.jsonl'
cdx=json.load(open(D+'/cdx_all.json'))
KEEP=re.compile(r'^/category/(sale|(mens|womens|kids|boys|girls)/(shoes|clothing)|(mens|womens|kids)/shoes/[a-z-]+|mens|womens|kids|shoes|clothing|brands/[a-z-]+|sale/[a-z/-]+)\.html$')
def ok(u):
    p=urllib.parse.urlsplit(u); q=urllib.parse.parse_qs(p.query)
    if not KEEP.match(p.path.lower()): return False
    return not any(k.lower() in('query','facets','q') or ':' in ''.join(v) for k,v in q.items())
sel={}
for d,rows in cdx.items():
    for ts,u in rows:
        if not ok(u): continue
        p=urllib.parse.urlsplit(u); key=(d,p.path.lower())
        sel.setdefault(key,{})
        # one capture/day per path; prefer no-query
        k=(ts[:8]); cur=sel[key].get(k)
        if cur is None or (p.query=='' and urllib.parse.urlsplit(cur[1]).query!=''): sel[key][k]=(ts,u)
done=set()
if os.path.exists(OUT):
    for l in open(OUT):
        r=json.loads(l); done.add((r['dom'],r['path'],r['ts']))
jobs=[(d,p,ts,u) for (d,p),m in sel.items() for ts,u in m.values() if (d,p,ts) not in done]
print('paths',len(sel),'jobs',len(jobs),flush=True)
def work(j):
    d,p,ts,u=j
    b=w.get('https://web.archive.org/web/%sid_/%s'%(ts,u),tries=4,timeout=60)
    rec={'dom':d,'path':p,'ts':ts,'url':u}
    if not b: rec['err']='fetch'; return rec
    s=b.decode('utf-8','replace'); o=P.find_search(s)
    if not o: rec['err']='noobj'; return rec
    rec['pag']=o.get('pagination'); rec['facets']=P.facet_map(o)
    prods=[]
    for pr in o.get('products',[]) or []:
        vs=[]
        for v in pr.get('variantOptions',[]) or []:
            vp=v.get('price') or {}
            vs.append([vp.get('listPrice'),vp.get('salePrice'),(v.get('flagsAndRestrictions') or {}).get('saleProduct'),v.get('newArrivalDate')])
        prods.append({'n':pr.get('name'),'sku':pr.get('sku'),'op':(pr.get('originalPrice') or {}).get('value'),'p':(pr.get('price') or {}).get('value'),'v':vs})
    rec['prods']=prods
    return rec
with cf.ThreadPoolExecutor(6) as ex, open(OUT,'a') as f:
    for i,r in enumerate(ex.map(work,jobs)):
        f.write(json.dumps(r)+'\n'); f.flush()
        if i%50==0: print(i,r['dom'],r['path'],r['ts'],r.get('err') or r['pag']['totalResults'],flush=True)
