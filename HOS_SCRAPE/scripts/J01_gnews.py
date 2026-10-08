import requests,re,sys,html
from email.utils import parsedate_to_datetime
qs=["Dick's House of Sport Gilbert San Tan Village grand opening","Dick's House of Sport Thornton Colorado grand opening August","Dick's House of Sport Parks at Arlington grand opening July","Dick's House of Sport Annapolis Mall grand opening August 14","Dick's House of Sport Mobile Bel Air grand opening"]
for q in qs:
    r=requests.get('https://news.google.com/rss/search',params={'q':q,'hl':'en-US','gl':'US','ceid':'US:en'},headers={'User-Agent':'Mozilla/5.0'},timeout=30)
    items=re.findall(r'<item>(.*?)</item>',r.text,re.S)
    print('##',q)
    rows=[]
    for it in items[:40]:
        t=html.unescape(re.search(r'<title>(.*?)</title>',it,re.S).group(1)); d=re.search(r'<pubDate>(.*?)</pubDate>',it).group(1)
        rows.append((parsedate_to_datetime(d).date().isoformat(),t[:130]))
    for d,t in sorted(rows)[-7:]: print(d,t)
