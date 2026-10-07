# usage: python3 W07_fetch.py URL OUTNAME  -> saves html + prints readable text
import sys, re, html
from curl_cffi import requests
url, out = sys.argv[1], sys.argv[2]
r = requests.get(url, impersonate="chrome", timeout=60)
p = '/home/user/dks-research/FL_INVENTORY_SCRAPE/raw/W07/' + out
open(p, 'w').write(r.text)
t = re.sub(r'<script.*?</script>|<style.*?</style>|<noscript.*?</noscript>', ' ', r.text, flags=re.S)
t = re.sub(r'<[^>]+>', ' ', t); t = re.sub(r'\s+', ' ', html.unescape(t))
print(r.status_code, len(r.text))
n = int(sys.argv[3]) if len(sys.argv) > 3 else 8000
kw = sys.argv[4] if len(sys.argv) > 4 else None
if kw:
    i = t.find(kw); t = t[max(0, i-500):]
print(t[:n])
