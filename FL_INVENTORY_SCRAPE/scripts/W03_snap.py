"""For each target in cdx_targets.json pick ~2 captures/month (2024-01..2026-10), fetch id_ raw, parse, save rows."""
import W03_wb as w, W03_parse as P, json, sys, os, statistics as st
D='/home/user/dks-research/FL_INVENTORY_SCRAPE/raw/W03'
OUT=D+'/snap_parsed.jsonl'
done=set()
if os.path.exists(OUT):
    for l in open(OUT):
        r=json.loads(l); done.add((r['target'],r['ts']))
only=sys.argv[1:]  # optional target filter substrings
per_month=int(os.environ.get('PERMONTH','2'))
cdx=json.load(open(D+'/cdx_targets.json'))
def pick(rows):
    ok=[r[0] for r in rows if r[1]=='200' and r[0][:6]>='202401']
    bym={}
    for t in ok: bym.setdefault(t[:6],[]).append(t)
    sel=[]
    for m,ts in sorted(bym.items()):
        # spread: earliest and latest in month
        if per_month==1: sel.append(min(ts,key=lambda t:abs(int(t[6:8])-15)))
        else:
            sel += sorted({ts[0],ts[-1]})
    return sel
for tgt,rows in cdx.items():
    if only and not any(o in tgt for o in only): continue
    for ts in pick(rows):
        if (tgt,ts) in done: continue
        b=w.get('https://web.archive.org/web/%sid_/https://www.%s'%(ts,tgt))
        rec={'target':tgt,'ts':ts}
        if not b: rec['err']='fetch'; 
        else:
            s=b.decode('utf-8','replace'); o=P.find_search(s)
            if not o: rec['err']='noobj'; rec['len']=len(s); rec['title']=s[s.find('<title'):s.find('</title>')][:120]
            else:
                rec['pag']=o.get('pagination'); rec['facets']=P.facet_map(o)
                prods=[]
                for p in o.get('products',[]) or []:
                    op=(p.get('originalPrice') or {}).get('value'); pr=(p.get('price') or {}).get('value')
                    vs=[]
                    for v in p.get('variantOptions',[]) or []:
                        vp=v.get('price') or {}
                        vs.append([vp.get('listPrice'),vp.get('salePrice'),(v.get('flagsAndRestrictions') or {}).get('saleProduct'),v.get('newArrivalDate')])
                    prods.append({'n':p.get('name'),'sku':p.get('sku'),'op':op,'p':pr,'sale':(p.get('badges') or {}).get('isSale') if isinstance(p.get('badges'),dict) else None,
                                  'rev':(p.get('reviewRatings') or {}).get('reviews'),'v':vs})
                rec['prods']=prods
        if rec.get('err')=='fetch': print('FAIL',tgt,ts,flush=True); continue
        open(OUT,'a').write(json.dumps(rec)+'\n'); done.add((tgt,ts))
        print(tgt,ts,rec.get('pag',{}).get('totalResults') if 'pag' in rec else rec.get('err'),flush=True)
