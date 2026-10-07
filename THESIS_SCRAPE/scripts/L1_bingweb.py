"""L1: Bing WEB search RSS (format=rss) for DKS Built to Win / store operating model evidence.
Rerun: python THESIS_SCRAPE/scripts/L1_bingweb.py  -> raw/L1_bingweb.csv
"""
import requests, csv, re, html, time, urllib.parse, sys
from xml.etree import ElementTree as ET
H={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0 Safari/537.36'}
Q=sys.argv[1:] or [
 '"Built to Win" "DICK\'S Sporting Goods" store',
 '"Built to Win" Dick\'s teammates linkedin',
 '"Dick\'s Sporting Goods" "new store operating model"',
 '"Dick\'s" "Built to Win" "Team Captain"',
 '"Dick\'s Sporting Goods" "Team Captain" store role',
 '"Dick\'s Sporting Goods" "store operating model" Sliva',
 '"Rudy Hernandez" "Dick\'s Sporting Goods" stores',
 '"Ray Sliva" Best Buy "president of retail"',
 '"Dick\'s Sporting Goods" "teammate - operations"',
 '"Dick\'s Sporting Goods" seasonal hiring 2026 teammates',
 'site:linkedin.com "Built to Win" Dick\'s Sporting Goods',
 'site:sgbonline.com Dick\'s store operating model',
 'site:chainstoreage.com Dick\'s Sporting Goods store operating model',
 'site:retaildive.com Dick\'s Sporting Goods store labor',
]
rows=[]
for q in Q:
    u='https://www.bing.com/search?format=rss&q='+urllib.parse.quote(q)
    try:
        r=requests.get(u,headers=H,timeout=30)
        root=ET.fromstring(r.content)
        n=0
        for it in root.iter('item'):
            rows.append([q,it.findtext('pubDate'),it.findtext('title'),it.findtext('link'),html.unescape(it.findtext('description') or '')[:400]]); n+=1
        print(n,q)
    except Exception as e:
        print('ERR',q,str(e)[:100], r.status_code if 'r' in dir() else '')
    time.sleep(1.5)
with open(r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\L1_bingweb.csv','a',newline='',encoding='utf-8') as f:
    csv.writer(f).writerows(rows)
for x in rows: print('|',x[0][:40],'|',x[2][:100],'|',x[3][:110],'\n     ',x[4][:300].replace('\n',' '))
