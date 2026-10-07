"""X10_news_rss_monitor.py
Repeatable news monitor for DKS owned/vertical brands. Queries Google News RSS (public, no key) and Bing News RSS
for each query term, dedupes, keeps items with pubDate >= START, and writes a CSV sorted by date.
Rerun weekly: python X10_news_rss_monitor.py 2026-01-01
Output: PB_SCRAPE/raw/X10_news_rss_<date>.csv
"""
import requests, sys, csv, os, time, html, re
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone
from xml.etree import ElementTree as ET
START=datetime.fromisoformat((sys.argv[1] if len(sys.argv)>1 else "2026-01-01")).replace(tzinfo=timezone.utc)
Q=['"CALIA" Dick\'s','"VRST" Dick\'s','"DSG" "Dick\'s" brand','Maxfli','"Walter Hagen" golf','"Top-Flite" golf','"Tommy Armour" golf','"Alpine Design" Dick\'s',
   '"Fitness Gear" Dick\'s','"Nishiki" bike Dick\'s','"ETHOS" Dick\'s','"Dick\'s" "vertical brands"','"Dick\'s" "private label"','"Dick\'s" "owned brands"','"Dick\'s" "in-house brands"',
   '"Dick\'s Sporting Goods" "exclusive brand"','"Aimee Watters"','"Chad Kessler" Dick\'s','"Foot Locker" "private label"']
H={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"}
rows={}
for q in Q:
    for src,url in [("gnews","https://news.google.com/rss/search"),("bing","https://www.bing.com/news/search")]:
        params={"q":q,"hl":"en-US","gl":"US","ceid":"US:en"} if src=="gnews" else {"q":q,"format":"rss","count":"100"}
        try:
            r=requests.get(url,params=params,headers=H,timeout=30)
            root=ET.fromstring(r.content)
        except Exception as e:
            print("ERR",src,q,e); continue
        for it in root.iter("item"):
            t=(it.findtext("title") or "").strip(); l=(it.findtext("link") or "").strip(); pd=it.findtext("pubDate")
            try: d=parsedate_to_datetime(pd)
            except Exception: continue
            if d.tzinfo is None: d=d.replace(tzinfo=timezone.utc)
            if d<START: continue
            k=re.sub(r"\W+","",t.lower())[:90]
            if k not in rows: rows[k]=[d.date().isoformat(),src,q,html.unescape(t),l]
        time.sleep(1.0)
out=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","raw",f"X10_news_rss_{datetime.now().date()}.csv")
with open(out,"w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["date","engine","query","title","link"])
    for r in sorted(rows.values(),reverse=True): w.writerow(r)
print(len(rows),"items ->",out)
for r in sorted(rows.values(),reverse=True): print(r[0],"|",r[2][:25],"|",r[3][:150])
