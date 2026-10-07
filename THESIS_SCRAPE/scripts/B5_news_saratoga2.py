import requests,re,html,urllib.parse,time
H={'User-Agent':'Mozilla/5.0 (research; palazzolojustin@gmail.com)'}
qs=['Saratoga sporting goods store opens 2025','Clifton Park sporting goods store opening','Wilton Mall Dicks Sporting Goods','Saratoga County new distribution center 2025 jobs','Malta NY new store 2025 sporting','Saratoga Springs Labubu store','Saratoga trading card store opens 2025','Ballston Spa warehouse jobs 2025 retailer']
for q in qs:
    for eng,u in [('g','https://news.google.com/rss/search?q='+urllib.parse.quote(q)+'&hl=en-US&gl=US&ceid=US:en'),('b','https://www.bing.com/news/search?q='+urllib.parse.quote(q)+'&format=rss')]:
        try: t=requests.get(u,headers=H,timeout=30).text
        except Exception as e: print('ERR',e); continue
        items=re.findall(r'<item>.*?<title>(.*?)</title>.*?<pubDate>(.*?)</pubDate>',t,re.S)
        print('==',eng,q,len(items),flush=True)
        for ti,d in items[:10]: print('  ',d[5:16],'|',html.unescape(ti)[:130],flush=True)
        time.sleep(1)
