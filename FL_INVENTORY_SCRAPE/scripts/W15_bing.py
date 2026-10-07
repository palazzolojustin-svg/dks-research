# W15: Bing News RSS queries -> CSV with direct publisher URLs
import sys, time, urllib.parse, csv, subprocess, xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
OUT='/home/user/dks-research/FL_INVENTORY_SCRAPE/raw/W15/'
rows=[]
for q in sys.argv[1:]:
    url='https://www.bing.com/news/search?q='+urllib.parse.quote(q)+'&format=rss&count=100'
    fn=OUT+'bing_'+''.join(c if c.isalnum() else '_' for c in q)[:60]+'.xml'
    subprocess.run(['curl','-sS','-m','30','-A','Mozilla/5.0','-o',fn,url])
    try: items=ET.parse(fn).findall('.//item')
    except Exception as e: print('ERR',q,e); continue
    for i in items:
        try: d=parsedate_to_datetime(i.findtext('pubDate')).strftime('%Y-%m-%d')
        except: d=''
        l=i.findtext('link'); u=urllib.parse.parse_qs(urllib.parse.urlparse(l).query).get('url',[l])[0]
        rows.append((d,i.findtext('title'),u,(i.findtext('description') or '')[:300],q))
    time.sleep(1.5)
seen=set()
with open(OUT+'bing_all.csv','a',newline='') as f:
    w=csv.writer(f)
    for r in sorted(rows,reverse=True):
        if r[2] in seen: continue
        seen.add(r[2]); w.writerow(r)
        if r[0]>='2026-08-15': print(r[0],'|',r[1][:110],'|',r[2][:120])
