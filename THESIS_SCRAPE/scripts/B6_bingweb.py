"""B6: Bing WEB search RSS (format=rss) for DICK'S Sporting Goods x store-labor/store-tech vendors.
Rerun: python B6_bingweb.py [queries...]  -> appends raw/B6_bingweb.csv; prints results.
"""
import requests, csv, html, time, urllib.parse, sys, os
from xml.etree import ElementTree as ET
H={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0 Safari/537.36'}
OUT=r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\B6_bingweb.csv'
D="\"Dick's Sporting Goods\" "
Q=sys.argv[1:] or [D+v for v in [
 'UKG','Kronos','"Legion" workforce','Reflexis','Zebra handheld','WorkJam','Quinyx','"Blue Yonder" workforce','"Workday" scheduling',
 'Logile','Axonify','Beekeeper','RFID Avery Dennison','RFID Checkpoint','RFID Nedap','RFID "SML"','"electronic shelf labels"',
 '"self-checkout"','Simbe','Zippedi','"case study" store associates','"labor forecasting"','"workforce management"',
 '"store associates" app','"teammate app"','Theatro','"Zipline" retail','YOOBIC','"Google Cloud" AI','Microsoft "store teammates"',
 '"Manhattan Associates" stores','"ship-from-store" automation','"mobile POS"','"Apple" iPhone teammates','Salesforce stores','"Coach by DICK\'S"']]
rows=[]
for q in Q:
    u='https://www.bing.com/search?format=rss&count=30&q='+urllib.parse.quote(q)
    try:
        r=requests.get(u,headers=H,timeout=30)
        root=ET.fromstring(r.content); n=0
        for it in root.iter('item'):
            rows.append([q,it.findtext('pubDate'),it.findtext('title'),it.findtext('link'),html.unescape(it.findtext('description') or '')[:500]]); n+=1
        print(n,q)
    except Exception as e:
        print('ERR',q,str(e)[:100])
    time.sleep(1.5)
with open(OUT,'a',newline='',encoding='utf-8') as f:
    csv.writer(f).writerows(rows)
for x in rows: print('|',x[0][:45],'|',(x[2] or '')[:100],'|',(x[3] or '')[:120],'\n     ',x[4][:300].replace('\n',' '))
