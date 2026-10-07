# W15: fetch article(s) with curl_cffi, save html+text, print text
import sys, re
from curl_cffi import requests
from bs4 import BeautifulSoup
OUT='/home/user/dks-research/FL_INVENTORY_SCRAPE/raw/W15/'
maxc=int(sys.argv[1])
for u in sys.argv[2:]:
    try:
        r=requests.get(u,impersonate='chrome',timeout=40)
        fn=OUT+'art_'+re.sub(r'[^A-Za-z0-9]','_',u.split('//')[1])[:90]
        open(fn+'.html','w').write(r.text)
        s=BeautifulSoup(r.text,'lxml')
        for x in s(['script','style','nav','footer','header','aside']): x.decompose()
        t=s.find('article') or s.body or s
        ps=[p.get_text(' ',strip=True) for p in t.find_all(['p','h1','h2','h3','li','time'])]
        txt='\n'.join(p for p in ps if len(p)>25)
        open(fn+'.txt','w').write(txt)
        print('=====',r.status_code,r.url); print(txt[:maxc])
    except Exception as e: print('ERR',u,e)
