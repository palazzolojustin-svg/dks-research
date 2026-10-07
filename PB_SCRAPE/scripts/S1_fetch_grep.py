"""S1 fetch+grep: python S1_fetch_grep.py URL outname -> saves raw/S1_<outname>.txt and prints owned-brand hits"""
import requests,sys,re
from bs4 import BeautifulSoup
url,name=sys.argv[1],sys.argv[2]
pat=sys.argv[3] if len(sys.argv)>3 else r'private[- ]label|private brand|owned brand|own brand|exclusive brand|Freely|R\.O\.W|Magellan|\bBCG\b|vertical|penetration'
H={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36','Accept-Language':'en-US,en;q=0.9'}
r=requests.get(url,headers=H,timeout=40)
print('status',r.status_code,len(r.text))
t=BeautifulSoup(r.text,'html.parser').get_text('\n')
t=re.sub(r'\n\s*\n+','\n',t)
open(rf'C:\Users\palaz\Downloads\DKS_RESEARCH\PB_SCRAPE\raw\S1_{name}.txt','w',encoding='utf-8').write(url+'\n'+t)
print('chars',len(t))
for m in re.finditer(pat,t,re.I):
    s=max(0,m.start()-400); e=min(len(t),m.end()+400)
    print('>>>',t[s:e].replace('\n',' ')); print()
