import requests,time,csv,glob,re,pandas as pd
H={'User-Agent':'Research palazzolojustin@gmail.com'}
centers=["Arrowhead Towne Center","Baybrook Mall","Bel Air Mall","Boulevard Mall","Brandywine Town Center","Brandon Exchange","Cross Creek Mall","Crossgates Mall","Dadeland Mall","Eastview Mall","Fairfield Commons","Fashion Square Charlottesville","Freehold Raceway Mall","Galleria Dallas","Greenbrier Mall","International Plaza","Katy Mills","Kennesaw Town Center","Market Place Shopping Center Champaign","Mall of Louisiana","Newport Centre","NorthPark Mall Davenport","Oakdale Mall","Polaris Fashion Place","Prudential Center","Ridgedale Center","Ross Park Mall","Salem Mall at Rockingham Park","Southpark Mall Strongsville","Southpoint Durham","Viewmont Mall","West Town Mall","Colonie Center","Penn Square Mall","Woodland Hills Mall","Leawood Town Center","Rolling Oaks Mall","Empire Mall","Washington Square"]
centers=sorted(centers)
import json
json.dump(centers,open('raw/M02/centers.json','w'))
seen=set()
for f in glob.glob('../THESIS_SCRAPE/raw/B10_fts_hits.csv')+glob.glob('../THESIS_SCRAPE/raw/B9_fts*.csv'):
    d=pd.read_csv(f)
    for u in d['url']: 
        m=re.search(r'/data/(\d+)/(\d{18})',u); 
        if m: seen.add(m.group(2))
print(len(seen),'cached accessions')
rows=[]
for c in centers:
  for q in ['"%s" "Dick\'s"'%c]:
    for forms in ['424B2,424H,FWP,424B5,424B3,ABS-15G,10-D,ABS-EE,8-K','']:
      try:
        r=requests.get('https://efts.sec.gov/LATEST/search-index',params=dict(q=q,dateRange='custom',startdt='2019-01-01',enddt='2026-10-08',**({'forms':forms} if forms else {})),headers=H,timeout=40)
        j=r.json(); hits=j['hits']['hits']
      except Exception as e:
        print(c,forms[:3],'ERR',e); hits=[]
      for h in hits:
        s=h['_source']; acc=s['adsh'].replace('-','')
        rows.append(dict(center=c,form=s['form'],file_date=s['file_date'],acc=acc,id=h['_id'],cik=s['ciks'][0],name=s['display_names'][0][:50],new=acc not in seen))
      time.sleep(0.25)
df=pd.DataFrame(rows).drop_duplicates(['center','id'])
df.to_csv('data/M02_fts_hits.csv',index=False)
print(df.groupby('center').agg(n=('id','count'),new=('new','sum')).to_string())
