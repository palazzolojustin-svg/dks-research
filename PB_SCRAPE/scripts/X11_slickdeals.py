"""X11 Slickdeals RSS: deal-post counts by month for DKS owned brands (promo-intensity proxy).
Rerun: python X11_slickdeals.py -> PB_SCRAPE/raw/X11_slickdeals.csv"""
import requests,re,collections,csv,email.utils,time,html
H={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36"}
rows=[]
for q in ["calia","vrst","dsg","maxfli","walter hagen","alpine design","nishiki","fitness gear","top flite"]:
    try:
        r=requests.get("https://slickdeals.net/newsearch.php",params={"q":q,"searcharea":"deals","searchin":"first","rss":"1"},headers=H,timeout=30)
    except Exception as e:
        print(q,"blocked/err",str(e)[:80]); time.sleep(15); continue
    items=re.findall(r"<item>(.*?)</item>",r.text,re.S)
    for it in items:
        t=re.search(r"<title><!\[CDATA\[(.*?)\]\]>",it,re.S); d=re.search(r"<pubDate>(.*?)</pubDate>",it)
        dt=email.utils.parsedate_to_datetime(d.group(1)) if d else None
        rows.append(dict(q=q,date=dt.date().isoformat() if dt else "",title=html.unescape(t.group(1)) if t else ""))
    time.sleep(12)
with open(r"C:\Users\palaz\Downloads\DKS_RESEARCH\PB_SCRAPE\raw\X11_slickdeals.csv","w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=["q","date","title"]); w.writeheader(); w.writerows(rows)
c=collections.Counter((r["q"],r["date"][:7]) for r in rows)
for q in sorted(set(r["q"] for r in rows)):
    ds=sorted(r["date"] for r in rows if r["q"]==q)
    print(q,len(ds),ds[0] if ds else "",ds[-1] if ds else "", sorted((k[1],v) for k,v in c.items() if k[0]==q))

