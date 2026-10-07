# decode Google News RSS article links to publisher URLs
import sys, re, json, urllib.parse
from curl_cffi import requests
def decode(link):
    aid=link.split('/articles/')[1].split('?')[0]
    r=requests.get('https://news.google.com/articles/'+aid,impersonate='chrome',timeout=30)
    sg=re.search(r'data-n-a-sg="([^"]+)"',r.text).group(1); ts=re.search(r'data-n-a-ts="([^"]+)"',r.text).group(1)
    req=[["Fbv4je",f'["garturlreq",[["X","X",["X","X"],null,null,1,1,"US:en",null,1,null,null,null,null,null,0,1],"X","X",1,[1,1,1],1,1,null,0,0,null,0],"{aid}",{ts},"{sg}"]']]
    r2=requests.post('https://news.google.com/_/DotsSplashUi/data/batchexecute',data={'f.req':json.dumps([req])},impersonate='chrome',timeout=30)
    t=r2.text.split('\n\n')[1]
    return json.loads(json.loads(t)[0][2])[1]
if __name__=='__main__':
    import csv
    pats=sys.argv[1:]
    for r in csv.reader(open('/home/user/dks-research/FL_INVENTORY_SCRAPE/raw/W15/gnews_all.csv')):
        if any(p.lower() in r[1].lower() for p in pats):
            try: print(r[0],'|',r[1][:90],'|',decode(r[3]))
            except Exception as e: print('ERR',r[1][:60],e)
