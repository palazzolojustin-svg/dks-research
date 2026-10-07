"""L1: Google News + Bing News RSS sweep for DKS store-operating-model / labor news.
Rerun: python THESIS_SCRAPE/scripts/L1_newsrss.py
Output: THESIS_SCRAPE/raw/L1_newsrss.csv (source, query, date, title, link, snippet)
"""
import requests, csv, re, html, time, urllib.parse
from xml.etree import ElementTree as ET
H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) research-bot palazzolojustin@gmail.com'}
Q = [
 '"DICK\'S Sporting Goods" "Built to Win"',
 '"Dick\'s Sporting Goods" "store operating model"',
 '"Dick\'s Sporting Goods" teammates store model 2026',
 '"Dick\'s Sporting Goods" "store managers"',
 '"Dick\'s Sporting Goods" layoffs 2026',
 '"Dick\'s Sporting Goods" layoffs stores',
 '"Dick\'s Sporting Goods" restructuring store employees',
 '"Dick\'s Sporting Goods" "Ray Sliva"',
 '"Rudy Hernandez" "Dick\'s"',
 '"Dick\'s Sporting Goods" seasonal hiring 2026',
 '"Dick\'s Sporting Goods" "National Signing Day" 2026',
 '"Dick\'s Sporting Goods" seasonal teammates',
 '"Dick\'s Sporting Goods" AI store labor scheduling',
 '"Dick\'s Sporting Goods" "store labor"',
 '"Dick\'s Sporting Goods" specialists footwear golf store',
 '"Dick\'s Sporting Goods" "assistant store manager"',
 '"Dick\'s Sporting Goods" wages raise employees',
 '"Dick\'s Sporting Goods" "Team Captain"',
 'DKS "operating model" severance stores',
 '"Dick\'s Sporting Goods" SG&A leverage 2027',
 '"Dick\'s Sporting Goods" "store payroll"',
 '"Dick\'s Sporting Goods" "labor model"',
 '"Lauren Hobart" stores labor AI',
 '"Navdeep Gupta" SG&A',
 '"Dick\'s Sporting Goods" "self-checkout"',
 '"Dick\'s Sporting Goods" employees demoted',
 '"Dick\'s" "Built to Win" teammates',
 '"Julie Lodge-Jarrett" 2026',
]
rows=[]
def gnews(q):
    u='https://news.google.com/rss/search?q='+urllib.parse.quote(q)+'&hl=en-US&gl=US&ceid=US:en'
    r=requests.get(u,headers=H,timeout=30)
    out=[]
    try:
        root=ET.fromstring(r.content)
        for it in root.iter('item'):
            out.append(('gnews',q,it.findtext('pubDate'),it.findtext('title'),it.findtext('link'),re.sub(r'<[^>]+>',' ',html.unescape(it.findtext('description') or ''))[:300]))
    except Exception as e:
        print('gnews err',q,r.status_code,r.text[:200])
    return out
def bing(q):
    u='https://www.bing.com/news/search?q='+urllib.parse.quote(q)+'&format=rss'
    r=requests.get(u,headers=H,timeout=30)
    out=[]
    try:
        root=ET.fromstring(r.content)
        for it in root.iter('item'):
            out.append(('bing',q,it.findtext('pubDate'),it.findtext('title'),it.findtext('link'),re.sub(r'<[^>]+>',' ',html.unescape(it.findtext('description') or ''))[:300]))
    except Exception as e:
        print('bing err',q,r.status_code,r.text[:200])
    return out
for q in Q:
    for fn in (gnews,bing):
        try:
            res=fn(q); rows+=res; print(fn.__name__, len(res), q)
        except Exception as e: print('ERR',q,e)
        time.sleep(1.0)
with open(r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\L1_newsrss.csv','w',newline='',encoding='utf-8') as f:
    w=csv.writer(f); w.writerow(['src','query','date','title','link','snippet']); w.writerows(rows)
print('total',len(rows))
