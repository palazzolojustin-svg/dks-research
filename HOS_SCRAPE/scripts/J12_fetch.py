import sys,re
from curl_cffi import requests
from bs4 import BeautifulSoup
urls=sys.argv[2:]; pat=re.compile(sys.argv[1],re.I)
for u in urls:
    try:
        r=requests.get(u,impersonate="chrome",timeout=30)
        t=BeautifulSoup(r.text,'lxml').get_text(' ',strip=True)
        open('raw/J12/'+re.sub(r'\W+','_',u)[-80:]+'.txt','w').write(t)
        print('##',u,r.status_code,len(t))
        for m in list(pat.finditer(t))[:6]:
            print('   ..',t[max(0,m.start()-200):m.end()+250].replace('\n',' '))
    except Exception as e: print('ERR',u,e)
