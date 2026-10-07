"""L2: fetch full Reddit threads (post + comments) via public Atom feed <post_url>.rss?limit=100.
Usage: python scripts/L2_reddit_threads.py <url_or_id> [...]   -> prints & appends to raw/L2_reddit_threads.jsonl
       python scripts/L2_reddit_threads.py --from-csv [regex]   -> all posts in raw/L2_reddit_posts.csv whose title/text matches regex
Note: comment feed gives comment text, author, date (no scores).
"""
import requests, feedparser, time, json, re, sys, os, html, csv
from bs4 import BeautifulSoup

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, 'raw')
H = {'User-Agent': 'research-script/0.1 (DKS labor model study; contact palazzolojustin@gmail.com)'}
OUT = os.path.join(RAW, 'L2_reddit_threads.jsonl')


def clean(t):
    t = BeautifulSoup(html.unescape(t or ''), 'html.parser').get_text(' ')
    t = re.sub(r'submitted by .*?\[link\] \[comments\]', '', t)
    return re.sub(r'\s+', ' ', t).strip()


def fetch(url):
    if not url.startswith('http'):
        url = f'https://www.reddit.com/comments/{url}/'
    u = url.rstrip('/') + '/.rss?limit=200'
    r = None
    for i in range(4):
        try:
            r = requests.get(u, headers=H, timeout=30)
        except Exception:
            time.sleep(30); continue
        if r.status_code == 429:
            time.sleep(45); continue
        break
    time.sleep(4)
    if r is None:
        return {'url': url, 'error': 'conn'}
    if r.status_code != 200:
        return {'url': url, 'error': r.status_code}
    f = feedparser.parse(r.text)
    items = []
    for e in f.entries:
        items.append({'date': e.get('updated', ''), 'author': e.get('author', ''), 'title': e.get('title', ''),
                      'text': clean(e.get('content', [{}])[0].get('value', '') if e.get('content') else '')})
    return {'url': url, 'n_items': len(items), 'items': items}


def main():
    args = sys.argv[1:]
    urls = []
    if args and args[0] == '--ids':
        done = set()
        if os.path.exists(OUT):
            for line in open(OUT, encoding='utf-8'):
                try:
                    d = json.loads(line)
                    if 'items' in d: done.add(re.search(r'/comments/([a-z0-9]+)', d['url']).group(1))
                except Exception: pass
        urls = [i for i in args[1].split(',') if i and i not in done]
        args = ['--from-csv']  # quiet mode
    elif args and args[0] == '--from-csv':
        rx = re.compile(args[1] if len(args) > 1 else '.', re.I)
        done = set()
        if os.path.exists(OUT):
            for line in open(OUT, encoding='utf-8'):
                try: done.add(json.loads(line)['url'])
                except Exception: pass
        for row in csv.DictReader(open(os.path.join(RAW, 'L2_reddit_posts.csv'), encoding='utf-8')):
            if rx.search(row['title'] + ' ' + row['text']) and row['link'] not in done:
                urls.append(row['link'])
    else:
        urls = args
    with open(OUT, 'a', encoding='utf-8') as fh:
        for u in urls:
            d = fetch(u)
            fh.write(json.dumps(d, ensure_ascii=False) + '\n'); fh.flush()
            if len(args) and args[0] != '--from-csv':
                for it in d.get('items', []):
                    print('---', it['date'][:10], it['author'], '|', it['title'][:80])
                    print(it['text'][:3000])
            else:
                print(u, d.get('n_items', d.get('error')), flush=True)


if __name__ == '__main__':
    main()
