import requests,csv,glob,re,json,time
H={"User-Agent":"Research palazzolojustin@gmail.com"}
known=set()
for f in glob.glob('THESIS_SCRAPE/raw/B*.csv'):
    for l in open(f,errors='ignore'):
        known.update(re.findall(r'/data/\d+/(\d{18})/',l))
print(len(known),'known accessions')
rows={}
qs=['"Dick\'s Sporting Goods"','"DICK\'S Sporting Goods"','"House of Sport"','"Dick\'s House of Sport"','"Golf Galaxy"','"Foot Locker"','"Champs Sports"','"DSG"']
for q in qs:
  for forms in ['','FWP,424B2,424H,424B5,424B3,ABS-15G,10-D,8-K']:
    for p in range(0,3):
      u=f'https://efts.sec.gov/LATEST/search-index?q={q}&dateRange=custom&startdt=2026-06-01&enddt=2026-10-08&from={p*100}'+(f'&forms={forms}' if forms else '')
      r=requests.get(u,headers=H);time.sleep(.25)
      if r.status_code!=200: print(q,r.status_code);break
      hs=r.json()['hits']['hits']
      for h in hs:
        s=h['_source'];rows[h['_id']]=(s['file_date'],s['form'],s['display_names'][0][:40],h['_id'])
      if len(hs)<100:break
print(len(rows))
out=[]
for k,v in sorted(rows.items(),key=lambda x:x[1]):
    acc=k.split(':')[0].replace('-','')
    out.append(v+(acc in known,))
json.dump(out,open('HOS_SCRAPE/raw/M04/hits.json','w'))
from collections import Counter
print(Counter((o[1],o[4]) for o in out))
for o in out:
    if o[1] not in('8-K','10-D','10-K','10-Q','4','3','SC 13G','DEF 14A') : print(o)
