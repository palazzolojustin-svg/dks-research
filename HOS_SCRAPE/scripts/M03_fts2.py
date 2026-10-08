import requests,time,csv,re,glob
H={'User-Agent':'Research palazzolojustin@gmail.com'}
known=set()
for f in glob.glob('../THESIS_SCRAPE/raw/B*_*.csv')+glob.glob('../THESIS_SCRAPE/raw/H04*.csv')+['data/M03_fts_hits.csv']:
    for m in re.findall(r'/data/(\d+)/(\d{18})/',open(f,encoding='utf-8',errors='ignore').read()): known.add(m[1])
cities=['Johnson City, NY','Kennesaw, GA','Knoxville, TN','Latham, NY','Leawood, KS','San Antonio, TX','Miami, FL','Minnetonka, MN','Mobile, AL','Oklahoma City, OK','Pittsburgh, PA','Salem, NH','Scranton, PA','Strongsville, OH','Tampa, FL','Tulsa, OK','Victor, NY','Wilmington, DE','Amherst','Beavercreek']
extra=['"Ross Park Mall"','"Rockingham Park"','"Fairfield Commons"','"Mall of Louisiana"','"Oakdale Mall"','"Eastview Mall"','"Quail Springs"','"Penn Square"','"Woodland Hills"','"Bel Air Mall"','"Brandywine"','"Town Center at Cobb"','"Dadeland"','"Viewmont"','"Colonie Center"','"Latham Farms"','"Rolling Oaks"','"Shops at Park Lane"','"Crabtree"']
qs=[f'"House of Sport" "{c}"' for c in cities[:18]]+[f'{e} "Dick\'s"' for e in extra]
new={}
for q in qs:
  for kw in ({},):
    try:j=requests.get('https://efts.sec.gov/LATEST/search-index',params={'q':q,'dateRange':'custom','startdt':'2019-01-01','enddt':'2026-10-08'},headers=H,timeout=30).json()
    except Exception as e: print('ERR',q);continue
    n=0
    for h in j.get('hits',{}).get('hits',[]):
        s=h['_source'];acc=s['adsh'].replace('-','')
        if acc in known: continue
        new.setdefault(acc,(s['file_date'],s['form'],s['display_names'][0][:35],h['_id'],[]))[4].append(q[:30]);n+=1
    time.sleep(.25)
for a,v in sorted(new.items(),key=lambda x:x[1][0]): print(v[0],v[1],v[2],v[3][:50],v[4][:2])
print(len(new))
