"""S1 search helper: python S1_search.py "query" -> prints top links from DDG html / Bing"""
import requests, sys, re, urllib.parse
from bs4 import BeautifulSoup
q=sys.argv[1]
H={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36','Accept-Language':'en-US,en;q=0.9'}
out=[]
try:
    r=requests.post('https://html.duckduckgo.com/html/',data={'q':q},headers=H,timeout=20)
    s=BeautifulSoup(r.text,'html.parser')
    for a in s.select('a.result__a'):
        href=a.get('href'); 
        m=re.search(r'uddg=([^&]+)',href or '')
        if m: href=urllib.parse.unquote(m.group(1))
        sn=a.find_parent('div',class_='result')
        snip=sn.select_one('.result__snippet').get_text(' ',strip=True) if sn and sn.select_one('.result__snippet') else ''
        out.append(('DDG',a.get_text(strip=True),href,snip))
except Exception as e: print('DDG err',e)
if not out:
    try:
        r=requests.get('https://www.bing.com/search',params={'q':q},headers=H,timeout=20)
        s=BeautifulSoup(r.text,'html.parser')
        for li in s.select('li.b_algo'):
            a=li.select_one('h2 a'); p=li.select_one('p')
            if a: out.append(('BING',a.get_text(strip=True),a.get('href'),p.get_text(' ',strip=True) if p else ''))
    except Exception as e: print('Bing err',e)
for o in out[:12]: print(' | '.join(o)[:500])
print('n=',len(out))
