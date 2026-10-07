"""L2: Bing web-search RSS + Bing News RSS + Google News RSS snippet harvester.
Usage: python scripts/L2_bing_rss.py "query 1" "query 2" ...   (prints; appends to raw/L2_search_snippets.jsonl)
Flags: --news (Bing News only), --gnews (Google News only); default = Bing web RSS.
"""
import requests, feedparser, sys, json, os, time, re, html
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, 'raw', 'L2_search_snippets.jsonl')
H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) research script contact palazzolojustin@gmail.com'}


def run(q, mode):
    if mode == 'news':
        url, params = 'https://www.bing.com/news/search', {'q': q, 'format': 'rss', 'count': 50}
    elif mode == 'gnews':
        url, params = 'https://news.google.com/rss/search', {'q': q, 'hl': 'en-US', 'gl': 'US', 'ceid': 'US:en'}
    else:
        url, params = 'https://www.bing.com/search', {'q': q, 'format': 'rss', 'count': 50}
    r = requests.get(url, params=params, headers=H, timeout=30)
    time.sleep(1.5)
    f = feedparser.parse(r.text)
    res = []
    for e in f.entries:
        s = re.sub(r'<[^>]+>', ' ', html.unescape(e.get('summary', '')))
        res.append({'q': q, 'mode': mode, 'date': e.get('published', ''), 'title': e.get('title', ''), 'link': e.get('link', ''), 'snippet': re.sub(r'\s+', ' ', s).strip()})
    return r.status_code, res


if __name__ == '__main__':
    args = sys.argv[1:]
    if args and args[0] == '--file':
        args = [l.strip() for l in open(args[1], encoding='utf-8-sig') if l.strip()]
    mode = 'web'
    if args and args[0] in ('--news', '--gnews'):
        mode = args[0][2:]; args = args[1:]
    with open(OUT, 'a', encoding='utf-8') as fh:
        for q in args:
            try:
                st, res = run(q, mode)
            except Exception as ex:
                print('## ERR', q, ex); continue
            print(f'## [{mode}] {q} -> {st}, {len(res)} results')
            for x in res:
                fh.write(json.dumps(x, ensure_ascii=False) + '\n')
                print(' -', x['date'][:16], '|', x['title'][:110], '|', x['link'][:150])
                print('    ', x['snippet'][:400])
