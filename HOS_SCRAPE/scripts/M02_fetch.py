import requests,re,time,pandas as pd,sys
H={'User-Agent':'Research palazzolojustin@gmail.com'}
d=pd.read_csv('data/M02_fts_hits.csv')
first=sorted(d.center.unique())[:20]
x=d[d.center.isin(first)&d.new&d.form.isin(['FWP','424B3','424H','424B2'])|((d.center=='Brandywine Town Center')&d.new&(d.file_date>'2026'))]
x=x[~x['name'].str.contains('CBL')]
for _,r in x.drop_duplicates('id').iterrows():
    acc,fn=r.id.split(':'); 
    u=f"https://www.sec.gov/Archives/edgar/data/{int(r.cik) if str(r.cik).isdigit() else r.cik}/{acc.replace('-','')}/{fn}"
    t=requests.get(u,headers=H,timeout=60).text; time.sleep(.3)
    open(f"raw/M02/{acc}_{fn}",'w').write(t)
    tx=re.sub(r'<[^>]+>',' ',t); tx=re.sub(r'\s+',' ',tx)
    print('=====',r.center,r['name'][:40],r.file_date,u,len(tx))
    n=0
    for m in re.finditer(r"Dick.?s",tx):
        s=tx[max(0,m.start()-250):m.end()+450]
        if re.search(r'sales|Sales|House of Sport',s): print('  >>',s); n+=1
        if n>=4:break
