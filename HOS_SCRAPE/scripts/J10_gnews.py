import requests,re,json,sys,urllib.parse,time
import xml.etree.ElementTree as ET
cities=["Miami Kendall","Minnetonka Ridgedale","Mobile Alabama","Nashville","Oklahoma City","Pittsburgh Ross Park","Raleigh Crabtree","Sacramento","Salem New Hampshire","San Antonio Live Oak","San Jose","Sarasota","Scranton","Sioux Falls","Springfield Missouri","Strongsville","Tampa","Tulsa","Victor New York","Wilmington Delaware Brandywine","Orlando","Phoenix","Rochester","Syracuse","Richmond","St. Louis","Pittsford","Texas","Virginia Beach","Rockford","Wichita","Reno","Tucson","Salt Lake","Seattle","Toledo","Rhode Island"]
out={}
for c in cities:
    q=f'"House of Sport" Dick\'s {c} hiring OR jobs OR employees OR teammates'
    u="https://news.google.com/rss/search?q="+urllib.parse.quote(q)+"&hl=en-US&gl=US&ceid=US:en"
    try:
        r=requests.get(u,timeout=20,headers={"User-Agent":"Mozilla/5.0"})
        root=ET.fromstring(r.content)
        items=[(i.findtext('pubDate')[:16],i.findtext('title'),i.findtext('link'),i.findtext('description')) for i in root.iter('item')]
    except Exception as e:
        items=[];print(c,e)
    out[c]=items
    time.sleep(1)
json.dump(out,open('raw/J10/gnews.json','w'))
seen=set()
for c,it in out.items():
    for d,t,l,_ in it:
        if t in seen: continue
        seen.add(t)
        if re.search(r'hir|job|employ|teammate|workers|staff|career',t,re.I) and re.search(r'house of sport|dick',t,re.I):
            print(c[:12],'|',d,'|',t[:140])
