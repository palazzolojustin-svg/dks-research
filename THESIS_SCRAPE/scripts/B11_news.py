"""B11 news search via Google News RSS + Bing News RSS. Usage: python scripts/B11_news.py "query" ["query2" ...]"""
import sys, requests, feedparser, urllib.parse
H = {'User-Agent': 'Mozilla/5.0 research palazzolojustin@gmail.com'}
for q in sys.argv[1:]:
    print('######', q)
    for base in ['https://news.google.com/rss/search?q={}&hl=en-US&gl=US&ceid=US:en', 'https://www.bing.com/news/search?q={}&format=rss']:
        try:
            r = requests.get(base.format(urllib.parse.quote(q)), headers=H, timeout=40)
            f = feedparser.parse(r.content)
            for e in f.entries[:15]:
                print(' -', e.get('published', '')[:16], '|', e.title[:140], '|', e.link[:160])
        except Exception as ex:
            print('ERR', base[:30], ex)
