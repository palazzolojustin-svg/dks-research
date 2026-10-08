import requests,time,csv,glob,re,json,sys
H={'User-Agent':'Research palazzolojustin@gmail.com'}
malls={ 'Johnson City':['Oakdale Mall','Oakdale Commons'],'Kennesaw':['Town Center at Cobb'],'Knoxville':['West Town Mall'],
'Latham':['Latham Farms','Latham Circle'],'Leawood':['Town Center Plaza Leawood'],'Live Oak':['Rolling Oaks Mall','Live Oak Marketplace'],
'Miami':['Dadeland Mall'],'Minnetonka':['Ridgedale Center'],'Mobile':['Bel Air Mall'],'OKC':['Quail Springs Mall','Penn Square Mall'],
'Pittsburgh':['Ross Park Mall'],'Salem NH':['Mall at Rockingham Park','Rockingham Park'],'Scranton':['Viewmont Mall'],
'Strongsville':['SouthPark Mall'],'Tampa':['International Plaza'],'Tulsa':['Woodland Hills Mall'],'Victor':['Eastview Mall','Victor Marketplace'],
'Wilmington':['Brandywine Town Center','Concord Mall','Christiana Mall']}
known=set()
for f in glob.glob('../THESIS_SCRAPE/raw/B*_*.csv')+glob.glob('../THESIS_SCRAPE/raw/H04*.csv'):
    for m in re.findall(r'/data/(\d+)/(\d{18})/',open(f,encoding='utf-8',errors='ignore').read()): known.add(m[1])
print(len(known),'known accessions')
rows={}
for city,ms in malls.items():
  for m in ms:
    for q in [f'"{m}" "Dick\'s"', f'"{m}" "DICK\'S Sporting Goods"']:
      try:
        r=requests.get('https://efts.sec.gov/LATEST/search-index',params={'q':q,'dateRange':'custom','startdt':'2019-01-01','enddt':'2026-10-08'},headers=H,timeout=30)
        j=r.json()
      except Exception as e:
        print('ERR',q,e); time.sleep(1); continue
      for h in j.get('hits',{}).get('hits',[]):
        s=h['_source']; id_=h['_id']; acc=s['adsh'].replace('-','')
        url=f"https://www.sec.gov/Archives/edgar/data/{int(s['ciks'][0])}/{acc}/{id_.split(':')[1]}"
        rows[(url)]=(city,m,s['file_date'],s['form'],s['display_names'][0][:40],acc in known)
      time.sleep(.25)
import csv
w=csv.writer(open('data/M03_fts_hits.csv','w'));w.writerow(['city','mall','date','form','filer','known_acc','url'])
for u,v in rows.items(): w.writerow(list(v)+[u])
from collections import Counter
print(Counter((v[0],v[5]) for v in rows.values()))
