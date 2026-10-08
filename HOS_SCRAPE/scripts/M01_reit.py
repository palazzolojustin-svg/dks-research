import csv,glob,re,requests,time,html
H={"User-Agent":"Research palazzolojustin@gmail.com"}
urls={}
for f in glob.glob('../THESIS_SCRAPE/raw/*.csv'):
    try:
        for row in csv.DictReader(open(f,errors='ignore')):
            u=row.get('url') or ''
            m=re.search(r'/data/(\d+)/(\d{18})/(.+)$',u)
            if m: urls[(m.group(2),m.group(3))]=u
    except: pass
r=[x for x in csv.DictReader(open('raw/M01/fts_hits.csv')) if x['form'] in('8-K','10-K','10-Q','ARS','DEF 14A') and not x['filer'].startswith(("DICK","FOOT"))]
seen=set()
for x in r:
    doc=x['id'].split(':')[1]; u=urls.get((x['acc'],doc))
    if not u: print('nourl',x['id'],x['filer'][:20]); continue
    t=requests.get(u,headers=H,timeout=60).text; time.sleep(.2)
    t=html.unescape(re.sub(r'<[^>]+>',' ',t)); t=re.sub(r'\s+',' ',t)
    for m in re.finditer(r'House of Sports?',t):
        s=t[max(0,m.start()-220):m.end()+260]; k=re.sub(r'\W','',s)[60:140]
        if k in seen: continue
        seen.add(k); print(x['date'],x['filer'][:14],'|',s,'\n')
