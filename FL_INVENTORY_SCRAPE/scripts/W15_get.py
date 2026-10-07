import sys,re
from curl_cffi import requests as r
for u in sys.argv[1:]:
    try:
        x=r.get(u,impersonate="chrome",timeout=30)
        t=re.sub(r'<script.*?</script>|<style.*?</style>','',x.text,flags=re.S);t=re.sub(r'<[^>]+>','\n',t);t=re.sub(r'\n\s*\n+','\n',t)
        open('raw/W15/get_'+re.sub(r'\W+','_',u)[-60:]+'.txt','w').write(t)
        print('=====',u,x.status_code,len(t));print(t[:6000])
    except Exception as e: print(u,e)
