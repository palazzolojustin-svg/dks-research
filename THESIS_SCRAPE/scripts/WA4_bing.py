"""WA4: Bing News RSS quick search. Rerun: python THESIS_SCRAPE\\scripts\\WA4_bing.py "q1" "q2" ... (prints top 8 with descriptions)."""
import sys, requests, urllib.parse, xml.etree.ElementTree as ET, json, os
H = {'User-Agent': 'Mozilla/5.0 (research; palazzolojustin@gmail.com)'}
BASE = os.path.join(os.path.dirname(__file__), '..', 'raw')
path = os.path.join(BASE, 'WA4_bing.json')
store = json.load(open(path)) if os.path.exists(path) else []
n = int(os.environ.get('N', '8'))
for q in sys.argv[1:]:
    r = requests.get('https://www.bing.com/news/search?q=' + urllib.parse.quote(q) + '&format=rss', headers=H, timeout=30)
    try:
        items = list(ET.fromstring(r.content).iter('item'))
    except ET.ParseError:
        print('PARSE ERR', q); continue
    print('===', q, len(items))
    for it in items[:n]:
        d = {'q': q, 'date': it.findtext('pubDate'), 'title': it.findtext('title'), 'desc': it.findtext('description'), 'link': it.findtext('link')}
        store.append(d)
        print(' -', (d['date'] or '')[:16], '|', d['title'], '|', (d['desc'] or '')[:300])
json.dump(store, open(path, 'w'), indent=1)
