"""R3: Google News + Bing News RSS sweep for loan monitoring / sale docs mentioning DKS store sales.
Rerun: python R3_news.py -> raw/R3/R3_news.csv"""
import requests, csv, time, urllib.parse, re
from bs4 import BeautifulSoup
H={"User-Agent":"Mozilla/5.0 (research script; palazzolojustin@gmail.com)"}
Q=['"5th Street Station" Charlottesville sold','"5th Street Station" "House of Sport"','"5th Street Station" CBRE',
'"House of Sport" CMBS','"House of Sport" loan refinance mall','"House of Sport" "sales per square foot"','"House of Sport" shopping center sold',
'"Dick\'s House of Sport" anchored center acquired','"Ridgedale Center" loan','"Ridgedale Center" Brookfield refinance',
'"International Plaza" Tampa loan refinance','"Empire Mall" loan','"Cape Cod Mall" loan','"Shops at Mission Viejo" loan',
'"Hamburg Pavilion" loan','"Crossgates Mall" loan','"Freehold Raceway Mall" loan','"Washington Square" Macerich loan refinance',
'Trepp "Dick\'s Sporting Goods"','"CRED iQ" "Dick\'s Sporting Goods"','KBRA "Dick\'s Sporting Goods" mall','DBRS Morningstar "Dick\'s Sporting Goods"',
'"Dick\'s Sporting Goods" "tenant sales"','"House of Sport" "in sales"','"House of Sport" "million in sales"','"Dick\'s" "House of Sport" "first year" sales million',
'"Westroads Mall" loan','"Brandon Exchange" sold','"Oakdale Commons" sold','"Polaris Fashion Place" loan House of Sport','"Eastview Mall" House of Sport sales','"West Town Mall" House of Sport loan']
rows=[]
for q in Q:
    for src,url in [("gnews","https://news.google.com/rss/search?q="+urllib.parse.quote(q)+"&hl=en-US&gl=US&ceid=US:en"),("bing","https://www.bing.com/news/search?q="+urllib.parse.quote(q)+"&format=rss")]:
        try:
            r=requests.get(url,headers=H,timeout=30)
            s=BeautifulSoup(r.content,"xml")
            for it in s.find_all("item"):
                rows.append([q,src,(it.pubDate.text if it.pubDate else ""),it.title.text if it.title else "",it.link.text if it.link else "",BeautifulSoup(it.description.text if it.description else "","html.parser").get_text()[:300]])
        except Exception as e: print("err",q,src,e)
        time.sleep(0.7)
    print(q,len(rows),flush=True)
with open(r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\R3\R3_news.csv","w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["q","src","date","title","link","desc"]); w.writerows(rows)
