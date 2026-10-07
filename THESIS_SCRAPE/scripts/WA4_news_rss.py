"""WA4: Google News / Bing News RSS pulls (titles, dates, links) for a list of queries.
Rerun: python THESIS_SCRAPE\\scripts\\WA4_news_rss.py "<query1>" "<query2>" ...  -> appends to raw\\WA4_news_rss.json and prints.
"""
import sys, json, os, requests, urllib.parse
import xml.etree.ElementTree as ET

BASE = os.path.join(os.path.dirname(__file__), '..', 'raw')
H = {'User-Agent': 'Mozilla/5.0 (research; palazzolojustin@gmail.com)'}


def gnews(q):
    u = 'https://news.google.com/rss/search?q=' + urllib.parse.quote(q) + '&hl=en-US&gl=US&ceid=US:en'
    r = requests.get(u, headers=H, timeout=30)
    root = ET.fromstring(r.content)
    out = []
    for it in root.iter('item'):
        out.append({'q': q, 'src': 'gnews', 'title': it.findtext('title'), 'date': it.findtext('pubDate'), 'link': it.findtext('link')})
    return out


def bing(q):
    u = 'https://www.bing.com/news/search?q=' + urllib.parse.quote(q) + '&format=rss'
    r = requests.get(u, headers=H, timeout=30)
    try:
        root = ET.fromstring(r.content)
    except ET.ParseError:
        return []
    out = []
    for it in root.iter('item'):
        out.append({'q': q, 'src': 'bing', 'title': it.findtext('title'), 'date': it.findtext('pubDate'), 'link': it.findtext('link'), 'desc': it.findtext('description')})
    return out


if __name__ == '__main__':
    path = os.path.join(BASE, 'WA4_news_rss.json')
    allr = json.load(open(path)) if os.path.exists(path) else []
    for q in sys.argv[1:]:
        res = []
        for f in (gnews, bing):
            try:
                res += f(q)
            except Exception as e:
                print('ERR', f.__name__, q, e)
        allr += res
        print('=== ', q, len(res))
        for x in res[:25]:
            print(' -', (x['date'] or '')[:16], '|', x['title'], '|', (x.get('desc') or '')[:200].replace('\n', ' '))
    json.dump(allr, open(path, 'w'), indent=1)
