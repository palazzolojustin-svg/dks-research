import sys
sys.argv=['x','"Wilton Mall" 2025','"Wilton Mall" Dick\'s','"Saratoga" "sporting goods" opening','"Clifton Park" "sporting goods"','"Saratoga County" store opening 2025 sporting','"Wilton" "Dick\'s Sporting Goods"','"Saratoga Springs" "Dick\'s"','"Clifton Park" "Dick\'s Sporting Goods"','"Saratoga County" warehouse sporting goods jobs 2025','"Malta" "sporting goods" store']
exec(open('scripts/B5_news.py',encoding='utf-8').read().split('for q in sys.argv[1:]')[0])
import time,re,html,urllib.parse
for q in sys.argv[1:]:
    u='https://news.google.com/rss/search?q='+urllib.parse.quote(q)+'&hl=en-US&gl=US&ceid=US:en'
    t=get(u)
    items=re.findall(r'<item>.*?<title>(.*?)</title>.*?<pubDate>(.*?)</pubDate>',t,re.S)
    print('==',q,len(items),flush=True)
    for ti,d in items[:15]: print('  ',d[5:16],'|',html.unescape(ti)[:140],flush=True)
    time.sleep(1.5)
