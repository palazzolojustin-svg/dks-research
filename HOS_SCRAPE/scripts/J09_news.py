import requests,re,json,urllib.parse,sys
import xml.etree.ElementTree as ET
cities=["Amherst NY","Baton Rouge","Beavercreek","Boston Prudential","Brandon FL","Champaign","Charlottesville","Chesapeake","Columbus Polaris","Dallas Galleria","Davenport","Durham Southpoint","Fayetteville NC","Freehold","Glendale AZ","Houston Baybrook","Katy","Jersey City","Johnson City","Kennesaw","Knoxville","Latham","Leawood","Live Oak San Antonio","Hamilton","Lexington","Louisville","Las Vegas","Irvine","Indianapolis","Greenville","Jacksonville","Atlanta","Albany","Allentown","Asheville","Lancaster","Lubbock","Kansas City","Little Rock","Huntsville","Henderson","Hoover","Frisco","Fort Worth","Greensboro","Grand Rapids","Gainesville","Alpharetta","Lakeland"]
out={}
for c in cities:
    q=f'"House of Sport" {c} (hiring OR jobs OR "job fair" OR employees OR teammates)'
    r=requests.get("https://news.google.com/rss/search",params={"q":q,"hl":"en-US","gl":"US","ceid":"US:en"},timeout=30,headers={"User-Agent":"Mozilla/5.0"})
    try: root=ET.fromstring(r.content)
    except Exception as e: print(c,'err');continue
    items=[(i.findtext('title'),i.findtext('link'),i.findtext('pubDate')) for i in root.iter('item')]
    out[c]=items
    print('##',c,len(items))
    for t,l,p in items[:8]: print('  ',p[5:16],t[:110])
json.dump(out,open('raw/J09/gnews.json','w'))
