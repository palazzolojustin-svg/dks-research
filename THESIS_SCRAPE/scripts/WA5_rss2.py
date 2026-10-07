"""WA5: targeted RSS search. Rerun: python THESIS_SCRAPE/scripts/WA5_rss2.py "query1" "query2" ..."""
import requests, urllib.parse, sys
from xml.etree import ElementTree as ET
H = {'User-Agent': 'Mozilla/5.0'}
for q in sys.argv[1:]:
    print('=== ', q)
    for u in ['https://www.bing.com/news/search?q=' + urllib.parse.quote(q) + '&format=rss',
              'https://news.google.com/rss/search?q=' + urllib.parse.quote(q) + '&hl=en-US&gl=US&ceid=US:en']:
        try:
            root = ET.fromstring(requests.get(u, headers=H, timeout=30).content)
            for it in list(root.iter('item'))[:12]:
                l = it.findtext('link') or ''
                if 'bing.com' in l:
                    l = urllib.parse.parse_qs(urllib.parse.urlparse(l).query).get('url', [l])[0]
                print((it.findtext('pubDate') or '')[:16], '|', (it.findtext('title') or '')[:110], '|', l[:170])
        except Exception as e:
            print('ERR', e)
