import json,requests,re,time,os
from curl_cffi import requests as cr
H={"User-Agent":"Research palazzolojustin@gmail.com"}
o=json.load(open('HOS_SCRAPE/raw/M04/hits.json'))
cm=[r for r in o if r[0]>='2026-06-10' and r[1] in('FWP','424B2','424H','424B5') and ('Mortgage' in r[2] or 'BANK5' in r[2] or 'Benchmark' in r[2]or 'BBCMS' in r[2])]
pat=re.compile(r"(dick'?s|house of sport|foot ?locker|champs)",re.I)
for r in cm:
    acc,fn=r[3].split(':')
    cik=None
    # find cik via index
    u=f'https://efts.sec.gov/LATEST/search-index?q="{fn}"&dateRange=custom&startdt={r[0]}&enddt={r[0]}'
    path=f'HOS_SCRAPE/raw/M04/{acc}_{fn}'
    if not os.path.exists(path):
        # cik via ciks field
        for _ in range(5):
            rr=requests.get(f'https://efts.sec.gov/LATEST/search-index?q="Dick%27s%20Sporting%20Goods"&dateRange=custom&startdt={r[0]}&enddt={r[0]}&forms={r[1]}',headers=H).json()
            if 'hits' in rr:break
            time.sleep(3)
        if 'hits' not in rr: print('fail',r);continue
        for h in rr['hits']['hits']:
            if h['_id']==r[3]: cik=int(h['_source']['ciks'][0]);break
        if not cik: print('nocik',r);continue
        url=f'https://www.sec.gov/Archives/edgar/data/{cik}/{acc.replace("-","")}/{fn}'
        d=requests.get(url,headers=H);time.sleep(.2)
        open(path,'wb').write(d.content)
        open(path+'.url','w').write(url)
    t=re.sub(r'<[^>]+>',' ',open(path,errors='ignore').read());t=re.sub(r'\s+',' ',t)
    ms=[m.start() for m in pat.finditer(t)]
    print(r[0],r[1],r[2][:30],fn,len(t),'matches',len(ms))
