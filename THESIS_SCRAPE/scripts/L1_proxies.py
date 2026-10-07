"""L1: fetch DKS DEF 14A proxies (2018-2026) from EDGAR, save text, extract CEO pay ratio / median employee pay and labor-related passages.
Rerun: python THESIS_SCRAPE/scripts/L1_proxies.py
Output: THESIS_SCRAPE/raw/L1_proxy_<year>.txt ; prints extracted pay-ratio passages
"""
import requests, re, json, html, time
from bs4 import BeautifulSoup
H={'User-Agent':'DKS research palazzolojustin@gmail.com'}
R=r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw'
d=requests.get('https://data.sec.gov/submissions/CIK0001089063.json',headers=H,timeout=30).json()
fil=[]
def collect(rec):
    for i in range(len(rec['form'])):
        if rec['form'][i]=='DEF 14A':
            fil.append((rec['filingDate'][i],rec['accessionNumber'][i],rec['primaryDocument'][i]))
collect(d['filings']['recent'])
for f in d['filings'].get('files',[]):
    collect(requests.get('https://data.sec.gov/submissions/'+f['name'],headers=H,timeout=30).json())
fil=sorted(set(fil))
print(fil)
for date,acc,doc in fil:
    if date<'2018-01-01': continue
    url=f"https://www.sec.gov/Archives/edgar/data/1089063/{acc.replace('-','')}/{doc}"
    t=requests.get(url,headers=H,timeout=60).text
    txt=BeautifulSoup(t,'html.parser').get_text(' ')
    txt=re.sub(r'\s+',' ',txt)
    open(rf'{R}\L1_proxy_{date}.txt','w',encoding='utf-8').write(url+'\n'+txt)
    print('=====',date,url,len(txt))
    for m in re.finditer(r'(?i)(median (employee|associate|teammate)|pay ratio)',txt):
        print('  ..',txt[max(0,m.start()-300):m.start()+600])
        break
    time.sleep(0.5)
