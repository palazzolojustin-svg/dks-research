import re,sys
from curl_cffi import requests
urls=open(sys.argv[1]).read().split()
for u in urls:
    try:
        r=requests.get(u,impersonate="chrome",timeout=25)
        t=re.sub(r'<(script|style)[^>]*>.*?</\1>',' ',r.text,flags=re.S)
        t=re.sub(r'<[^>]+>',' ',t);t=re.sub(r'\s+',' ',t)
        open('raw/J10/'+re.sub(r'\W+','_',u)[-60:]+'.txt','w').write(t)
        print('##',r.status_code,u[:90],len(t))
        for m in re.finditer(r'[^.]*\b(jobs|employ\w*|hir\w+|team ?members|teammates|associates|staff\w*|workers|payroll|sales)\b[^.]*\.',t,re.I):
            s=m.group(0).strip()
            if re.search(r'\d',s) and len(s)<400: print('  -',s[:300])
    except Exception as e: print('##ERR',u[:80],e)
