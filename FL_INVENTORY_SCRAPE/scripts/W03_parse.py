"""Parse footlocker/champs category page HTML (live or Wayback) -> search result object (pagination, facets, products)."""
import re, json
DEC=json.JSONDecoder()
def find_search(s):
    out=[]
    for m in re.finditer(r'"pagination"\s*:\s*\{\s*"currentPage"',s):
        pi=m.start()
        # walk back over '{' candidates
        j=pi
        tries=0
        while tries<4000:
            j=s.rfind('{',0,j)
            if j<0: break
            tries+=1
            try:
                obj,end=DEC.raw_decode(s,j)
            except Exception:
                continue
            if end>pi and isinstance(obj,dict):
                if 'pagination' in obj:
                    out.append(obj); break
                else:
                    break
        if out: break
    return out[0] if out else None

def facet_map(obj):
    fm={}
    for f in obj.get('facets',[]) or []:
        code=f.get('code') or f.get('name')
        fm[code]={v.get('name'):v.get('count') for v in f.get('values',[]) or []}
    return fm

def prices(obj):
    rows=[]
    for p in obj.get('products',[]) or []:
        pr=p.get('price') or {}
        rows.append(dict(name=p.get('name'),sku=p.get('sku') or p.get('baseProduct'),
            orig=(pr.get('originalPrice') or pr.get('listPrice')),sale=(pr.get('salePrice') or pr.get('value')),
            isSale=(p.get('badges') or {}).get('isSale') if isinstance(p.get('badges'),dict) else None, raw=pr))
    return rows
if __name__=='__main__':
    import sys
    s=open(sys.argv[1],encoding='utf-8',errors='replace').read()
    o=find_search(s)
    if not o: print('NO SEARCH OBJ'); sys.exit()
    print(o['pagination'])
    fm=facet_map(o)
    for k,v in fm.items(): print(k, list(v.items())[:12])
    for r in prices(o)[:5]: print(r)
