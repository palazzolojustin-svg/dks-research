import requests,time,re,csv,glob,json,itertools
H={"User-Agent":"Research palazzolojustin@gmail.com"}
known=set()
for f in glob.glob('../THESIS_SCRAPE/raw/*.csv')+glob.glob('data/*.csv')+glob.glob('wave*/*.csv'):
    try: t=open(f,errors='ignore').read()
    except: continue
    known|=set(re.findall(r'/data/\d+/(\d{18})/',t)); known|=set(re.findall(r'\b(\d{18})\b',t))
print('known acc',len(known))
phr=['"House of Sport"','"House of Sports"',"\"DICK'S House of Sport\"","\"Dick's Sporting Goods House of Sport\"","\"DSG House of Sport\"","\"Dick's House of Sport\""]
forms=[None,'FWP','424B2','424B5','424B3','424H','10-D','ABS-15G','8-K','10-K','10-Q','EX-99','S-11','SC 13D']
yrs=[(f"{y}-01-01",f"{y}-06-30") for y in range(2021,2027)]+[(f"{y}-07-01",f"{y}-12-31") for y in range(2021,2027)]
hits={}
def q(p,form,s,e):
    for a in range(3):
        u=f'https://efts.sec.gov/LATEST/search-index?q={requests.utils.quote(p)}&dateRange=custom&startdt={s}&enddt={e}'+(f'&forms={form}' if form else '')
        r=requests.get(u,headers=H,timeout=30)
        if r.status_code==200: return r.json()
        time.sleep(1.5)
    return None
fail=0
for p in phr:
  for form in forms:
    for s,e in yrs:
      if form and form not in(None,) and p!=phr[0] and form not in('FWP','424B2','10-D') : continue
      j=q(p,form,s,e); time.sleep(0.22)
      if j is None: fail+=1; continue
      for h in j['hits']['hits']:
        i=h['_id']; src=h['_source']; acc=i.split(':')[0].replace('-','')
        hits.setdefault(i,(src['file_date'],src['form'],(src.get('display_names') or [''])[0][:60],acc,p))
print('fail',fail,'hits',len(hits))
rows=sorted(hits.items(),key=lambda x:x[1][0])
w=csv.writer(open('raw/M01/fts_hits.csv','w'))
w.writerow(['id','date','form','filer','acc','query','known'])
nn=0
for i,v in rows:
    k=v[3] in known; nn+=(not k)
    w.writerow([i,*v,k])
print('new docs',nn)
