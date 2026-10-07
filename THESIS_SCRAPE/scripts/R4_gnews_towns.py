"""R4: Google News RSS titles for HoS candidate towns. Rerun: python R4_gnews_towns.py > ..\\raw\\R4_gnews_towns.txt"""
import requests, urllib.parse
from bs4 import BeautifulSoup
UA = {'User-Agent': 'Mozilla/5.0 research palazzolojustin@gmail.com'}
towns = ['Cherry Hill', 'Tigard', 'Washington Square', 'King of Prussia', 'Upper Merion', 'Peabody', 'Schaumburg', 'Woodfield',
         'Arden Fair', 'Springfield Missouri', 'Battlefield Mall', 'Lubbock', 'Mission Valley', 'Sarasota', 'Galleria St. Louis',
         'Richmond Heights', 'Oakwood Plaza', 'Hollywood Florida', 'CoolSprings', 'Franklin Tennessee']
for t in towns:
    for q in [f'"House of Sport" "{t}"', f'"Dick\'s" "{t}" planning OR zoning OR council House of Sport']:
        r = requests.get('https://news.google.com/rss/search?q=' + urllib.parse.quote(q) + '&hl=en-US&gl=US&ceid=US:en', headers=UA, timeout=30)
        items = BeautifulSoup(r.content, 'xml').find_all('item')
        print(f'=== {q} ({len(items)})')
        for it in items[:12]:
            ti = it.title.text
            if 'sport' in ti.lower() or "dick" in ti.lower():
                print('  ', it.pubDate.text[5:16], '|', ti)
