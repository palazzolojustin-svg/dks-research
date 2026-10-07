"""W03 helper: robust Wayback fetch with retries + disk cache."""
import os, time, hashlib, requests, sys
CA='/root/.ccr/ca-bundle.crt'
RAW='/home/user/dks-research/FL_INVENTORY_SCRAPE/raw/W03/cache'
os.makedirs(RAW,exist_ok=True)
S=requests.Session()
S.headers['User-Agent']='Mozilla/5.0 (research; W03 wayback time series)'
def get(url, tries=12, timeout=90, cache=True, minsize=0):
    h=hashlib.md5(url.encode()).hexdigest()
    p=os.path.join(RAW,h)
    if cache and os.path.exists(p) and os.path.getsize(p)>minsize:
        return open(p,'rb').read()
    last=None
    for i in range(tries):
        try:
            r=S.get(url,timeout=timeout,verify=CA)
            if r.status_code==200:
                if cache: open(p,'wb').write(r.content)
                return r.content
            if r.status_code in (404,403):
                return None
            last=r.status_code
        except Exception as e:
            last=repr(e)[:120]
        time.sleep(min(4+i*3,30))
    print('FAIL',url,last,file=sys.stderr)
    return None
