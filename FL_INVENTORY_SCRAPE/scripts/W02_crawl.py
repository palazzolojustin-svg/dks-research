"""Crawl Champs / KFL / FL.ca catalog via server-rendered search pages (STATE_FROM_SERVER JSON).
Fastly caches by `query` param only (ignores currentPage), so each page gets a unique
percent-encoding of letters in the query string (server decodes identically).
usage: python3 -I W02_crawl.py <site> <label> <base_query e.g. :name-asc:collection_id:all-men-s> [path_prefix]"""
import sys, json, time, random, urllib.parse, os
sys.path.insert(0,'/home/user/dks-research/FL_INVENTORY_SCRAPE/scripts')
from W02_parse import extract_state, find_search
import subprocess
site, label, base = sys.argv[1], sys.argv[2], sys.argv[3]
prefix = sys.argv[4] if len(sys.argv)>4 else ''
OUT='/home/user/dks-research/FL_INVENTORY_SCRAPE/raw/W02'
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
class R: pass
def fetch(url):
    o=subprocess.run(['curl','-sS','--compressed','--max-time','60','-A',UA,url],capture_output=True)
    r=R(); r.text=o.stdout.decode('utf-8','replace'); r.status_code=o.returncode; return r
def enc(q, n, salt):
    # encode letters whose index bit is set in (n + salt*1000) pattern
    letters=[i for i,c in enumerate(q) if c.isalpha()]
    code=n*7919+salt*104729+12345
    out=[]
    for i,c in enumerate(q):
        if c.isalpha() and i in letters[:40] and (code>>(letters.index(i)%30))&1:
            out.append('%%%02X'%ord(c))
        else:
            out.append(urllib.parse.quote(c,safe=''))
    return ''.join(out)
def get(page, salt=0):
    for attempt in range(6):
        url=f'https://www.{site}{prefix}/search?query={enc(base,page,salt+attempt*17+int(time.time())%1000)}&currentPage={page}'
        try:
            r=fetch(url)
            st=extract_state(r.text); res=find_search(st) if st else None
            if res and res['pagination']['currentPage']==page: return res
            print('mismatch/none',page,r.status_code, res and res['pagination'], file=sys.stderr)
        except Exception as e:
            print('err',page,e,file=sys.stderr)
        time.sleep(2+attempt*2)
    return None
first=get(0)
tp=first['pagination']['totalPages']; tot=first['pagination']['totalResults']
print(label,'total',tot,'pages',tp, file=sys.stderr)
fo=open(f'{OUT}/{site}_{label}.jsonl','w')
json.dump({'_meta':True,'site':site,'label':label,'query':base,'pagination':first['pagination'],'facets':first['facets'],'time':first['metaData']},fo); fo.write('\n')
def dump(res,page):
    for p in res['products']:
        p['_page']=page; fo.write(json.dumps(p)+'\n')
dump(first,0)
for pg in range(1,tp):
    res=get(pg)
    if res: dump(res,pg)
    else: print('FAILED page',pg,file=sys.stderr)
    fo.flush(); time.sleep(0.4+random.random()*0.4)
print(label,'done',file=sys.stderr)
