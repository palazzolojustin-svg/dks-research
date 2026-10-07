import W03_wb as w, json, sys, time, os
OUT='/home/user/dks-research/FL_INVENTORY_SCRAPE/raw/W03/cdx_targets.json'
FL=['sale','shoes','clothing','mens','womens','kids','mens/shoes','womens/shoes','kids/shoes','mens/clothing','womens/clothing','kids/clothing',
    'mens/new-arrivals','womens/new-arrivals','kids/new-arrivals','new-arrivals','brands/nike','brands/jordan','brands/adidas','brands/new-balance',
    'brands/on','brands/hoka','brands/asics','brands/salomon','brands/ugg','brands/puma','brands/timberland','brands/crocs','brands/converse','brands/vans',
    'mens/nike','mens/jordan','mens/new-balance','mens/on','mens/hoka','mens/asics','brands/under-armour','brands/nike-jordan']
targets=[('footlocker.com/category/%s.html'%p) for p in FL]+[('champssports.com/category/%s.html'%p) for p in FL]
try: res=json.load(open(OUT))
except: res={}
import threading
from concurrent.futures import ThreadPoolExecutor
lock=threading.Lock()
def one(t):
    if t in res: return
    u='https://web.archive.org/cdx/search/cdx?url=%s&from=2023&to=2026&output=json&fl=timestamp,statuscode,length,digest&collapse=timestamp:8'%t
    b=w.get(u,cache=False)
    if b is None: print('fail',t); return
    try: rows=json.loads(b)[1:] if b.strip() else []
    except Exception as e: print('bad',t,b[:100]); return
    with lock:
        res[t]=rows
        json.dump(res,open(OUT+'.tmp','w')); os.replace(OUT+'.tmp',OUT)
    ok=[r for r in rows if r[1]=='200']
    print(t,len(rows),'200s:',len(ok),'months:',len({r[0][:6] for r in ok}),flush=True)

with ThreadPoolExecutor(4) as ex: list(ex.map(one,targets))
