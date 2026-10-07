# W15: pull Google News RSS for a list of queries, dedupe, save CSV
import sys, time, urllib.parse, csv, subprocess, xml.etree.ElementTree as ET, os
from email.utils import parsedate_to_datetime
OUT='/home/user/dks-research/FL_INVENTORY_SCRAPE/raw/W15/'
qs=sys.argv[1:]
rows=[]
for q in qs:
    url='https://news.google.com/rss/search?q='+urllib.parse.quote(q)+'&hl=en-US&gl=US&ceid=US:en'
    fn=OUT+'gn_'+''.join(c if c.isalnum() else '_' for c in q)[:60]+'.xml'
    subprocess.run(['curl','-sS','-m','30','-o',fn,url])
    try: items=ET.parse(fn).findall('.//item')
    except Exception as e: print('ERR',q,e); continue
    for i in items:
        d=parsedate_to_datetime(i.findtext('pubDate'))
        s=i.find('source')
        rows.append((d.strftime('%Y-%m-%d'),i.findtext('title'),s.text if s is not None else '',i.findtext('link'),q))
    time.sleep(1.5)
seen=set();out=[]
for r in sorted(rows,reverse=True):
    if r[1] in seen: continue
    seen.add(r[1]);out.append(r)
for r in out:
    if r[0]>='2026-08-25': print(r[0],'|',r[1],'|',r[4])
with open(OUT+'gnews_all.csv','a',newline='') as f:
    csv.writer(f).writerows(out)
