import re, json, sys, time
from curl_cffi import requests as cr
import requests
S = requests.Session()
S.headers.update({"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36","Accept":"text/html,application/xhtml+xml","Accept-Language":"en-US,en;q=0.9"})
BASE = "https://www.footlocker.com"
def get_html(url):
    for i in range(4):
        try:
            r = S.get(url, timeout=60)
            if r.status_code == 200: return r.text
            print("status", r.status_code, url, file=sys.stderr)
        except Exception as e:
            print("err", e, file=sys.stderr)
        time.sleep(3*(i+1))
    return None
def hydration(h):
    i = h.find('STATE_FROM_SERVER:')
    if i < 0: return None
    dec = json.JSONDecoder()
    j = h.index('{', i)
    obj, end = dec.raw_decode(h, j)
    return obj
def find_search(obj):
    # recursively find dict with 'pagination' and 'products'
    if isinstance(obj, dict):
        if 'pagination' in obj and 'products' in obj: return obj
        for v in obj.values():
            r = find_search(v)
            if r: return r
    elif isinstance(obj, list):
        for v in obj:
            r = find_search(v)
            if r: return r
    return None
def search(url):
    h = get_html(url)
    if h is None: return None
    d = hydration(h)
    if d is None:
        print("no hydration", url, file=sys.stderr); return None
    return find_search(d)
if __name__ == "__main__":
    s = search(sys.argv[1])
    print(json.dumps(s['pagination']), len(s['products']))
    print([f['code'] for f in s.get('facets',[])])
