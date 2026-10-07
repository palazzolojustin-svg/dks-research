# W15: fetch MSN article body via assets.msn.com content API
import sys,json,re
from curl_cffi import requests
from bs4 import BeautifulSoup
for aid in sys.argv[2:]:
    r=requests.get(f'https://assets.msn.com/content/view/v2/Detail/en-us/{aid}',impersonate='chrome',timeout=30)
    try: j=r.json()
    except: print('ERR',aid,r.status_code); continue
    open(f'/home/user/dks-research/FL_INVENTORY_SCRAPE/raw/W15/msn_{aid}.json','w').write(r.text)
    body=BeautifulSoup(j.get('body',''),'lxml').get_text('\n',strip=True)
    print('=====',aid,j.get('title'),'|',j.get('publishedDateTime'),'|',(j.get('provider') or {}).get('name'),'|',j.get('sourceHref'))
    print(body[:int(sys.argv[1])])
