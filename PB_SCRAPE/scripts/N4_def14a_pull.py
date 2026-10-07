"""N4: pull DKS DEF 14A filings from EDGAR (submissions API) and save plain text.
Rerun: python PB_SCRAPE/scripts/N4_def14a_pull.py  -> PB_SCRAPE/raw/N4_DEF14A_<date>.txt"""
import requests,re,json,os
from bs4 import BeautifulSoup
H={'User-Agent':'DKS research palazzolojustin@gmail.com'}
out=r"C:\Users\palaz\Downloads\DKS_RESEARCH\PB_SCRAPE\raw"
j=requests.get('https://data.sec.gov/submissions/CIK0001089063.json',headers=H,timeout=30).json()
r=j['filings']['recent']
rows=[(r['filingDate'][i],r['form'][i],r['accessionNumber'][i],r['primaryDocument'][i]) for i in range(len(r['form'])) if r['form'][i] in ('DEF 14A','DEFA14A')]
for x in rows[:12]: print(x)
for d,f,a,p in rows:
    if f!='DEF 14A' or d<'2022-01-01': continue
    url=f"https://www.sec.gov/Archives/edgar/data/1089063/{a.replace('-','')}/{p}"
    h=requests.get(url,headers=H,timeout=60).text
    t=BeautifulSoup(h,'html.parser').get_text(' ')
    t=re.sub(r'\s+',' ',t)
    fn=os.path.join(out,f"N4_DEF14A_{d}.txt"); open(fn,'w',encoding='utf-8').write(url+'\n'+t)
    print('saved',fn,len(t))
