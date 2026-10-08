import csv,requests,re,time,glob,html
H={"User-Agent":"Research palazzolojustin@gmail.com"}
urls={}
for f in glob.glob('../THESIS_SCRAPE/raw/*.csv'):
    try:
        for row in csv.DictReader(open(f,errors='ignore')):
            u=row.get('url') or ''
            m=re.search(r'/data/(\d+)/(\d{18})/(.+)$',u)
            if m: urls[(m.group(2),m.group(3))]=u
    except Exception as e: pass
r=[x for x in csv.DictReader(open('raw/M01/fts_hits.csv')) if x['form'] in('FWP','424B2','424H','424B5','424B3')]
out=open('raw/M01/ctx.txt','w'); miss=0;n=0
for x in r:
    doc,=[x['id'].split(':')[1]]; acc=x['acc']
    u=urls.get((acc,doc))
    if not u: miss+=1; out.write(f"## NOURL {x['id']} {x['filer'][:40]}\n"); continue
    try: t=requests.get(u,headers=H,timeout=60).text
    except Exception as e: out.write(f"## ERR {u}\n"); continue
    time.sleep(0.2)
    t=html.unescape(re.sub(r'<[^>]+>',' ',t)); t=re.sub(r'\s+',' ',t)
    ms=list(re.finditer(r'House of Sports?',t))
    out.write(f"## {x['date']} {x['form']} {x['filer'][:45]} {u} len={len(t)} hits={len(ms)}\n")
    last=-9999
    for m in ms:
        if m.start()-last<600: continue
        last=m.start()
        out.write("   > "+t[max(0,m.start()-250):m.end()+350]+"\n")
    n+=1
print(n,miss)
