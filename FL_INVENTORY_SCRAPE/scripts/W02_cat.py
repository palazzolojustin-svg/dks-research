import sys,re,urllib.parse
sys.path.insert(0,'/home/user/dks-research/FL_INVENTORY_SCRAPE/scripts')
from W02_parse import *
for f in sys.argv[1:]:
    s=open(f).read(); st=extract_state(s); r=find_search(st)
    if not r: print(f,'NO SEARCH'); continue
    q=None
    for fc in r.get('facets',[]):
        for v in fc.get('values',[]):
            u=v.get('query',{}).get('value','');
            if u: q=urllib.parse.unquote(u); break
        if q: break
    sale=[v['count'] for fc in r.get('facets',[]) for v in fc.get('values',[]) if v.get('name')=='Sale Product']
    print(f, r['pagination']['totalResults'], 'sale',sale, '|', q)
