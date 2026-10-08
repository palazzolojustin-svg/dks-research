import requests,time,re,csv,glob
H={"User-Agent":"Research palazzolojustin@gmail.com"}
known=set()
for f in glob.glob('../THESIS_SCRAPE/raw/*.csv')+glob.glob('raw/M01/fts_hits.csv')+glob.glob('wave*/*.csv'):
    known|=set(re.findall(r'\b(\d{18})\b',open(f,errors='ignore').read()))
qs=['DHOS','"DSG House of Sport"','"Dick\'s Sporting Goods" "flagship" "House of Sport"','"DICK\'S House of Sport" sales','"House of Sport" "tenant sales"','"House of Sport" "occupancy cost"','"House of Sport" "sales per square foot"','"House of Sport" "ground lease"','"House of Sport" "sublease"','"Dick\'s" "experiential" "House of Sport"','"House of Sport" "10-D"','"HoS" "Dick\'s Sporting Goods" sales','"Dick\'s Sporting Goods" "new prototype"','"House of Sports"','"House of Sport" "Foot Locker"','"Dick\'s" "Sears" "sublease" "Primark"']
new={}
for q in qs:
  for y in range(2021,2027):
    for fm in (None,):
      u=f'https://efts.sec.gov/LATEST/search-index?q={requests.utils.quote(q)}&dateRange=custom&startdt={y}-01-01&enddt={y}-12-31'
      for a in range(3):
        r=requests.get(u,headers=H,timeout=30)
        if r.status_code==200: break
        time.sleep(1.5)
      else: print('fail',q,y); continue
      time.sleep(.2)
      for h in r.json()['hits']['hits']:
        acc=h['_id'].split(':')[0].replace('-','')
        if acc in known or acc in new: continue
        s=h['_source']; new[acc]=(s['file_date'],s['form'],(s.get('display_names') or [''])[0][:45],h['_id'].split(':')[1],q)
for a,v in sorted(new.items(),key=lambda x:x[1][0]): print(a,v)
print(len(new))
