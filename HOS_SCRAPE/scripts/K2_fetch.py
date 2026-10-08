import re,sys,hashlib
from curl_cffi import requests
urls=sys.argv[1:]
for u in urls:
    try:
        r=requests.get(u,impersonate="chrome",timeout=30)
    except Exception as e:
        print("ERR",u,e);continue
    t=r.text
    open("/home/user/dks-research/HOS_SCRAPE/raw/K2/"+hashlib.md5(u.encode()).hexdigest()[:8]+".html","w").write(t)
    t=re.sub(r'<script.*?</script>|<style.*?</style>','',t,flags=re.S);t=re.sub(r'<[^>]+>',' ',t);t=re.sub(r'\s+',' ',t)
    print("==",r.status_code,len(t),u)
    seen=0
    for m in re.finditer(r'[^.]{0,160}\b(hir(e|ed|ing)|employ\w*|jobs|associates|team ?members|teammates|positions|workers|staff)\b[^.]{0,160}',t,flags=re.I):
        s=m.group(0)
        if re.search(r'\d{2,}',s) and seen<6: print('  >',s.strip()[:320]);seen+=1
