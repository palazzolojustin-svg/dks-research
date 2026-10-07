"""L2 Reddit RSS scraper (employee-side evidence on DKS 'Built to Win' store model).

Reddit's .json endpoints return 403 from this machine, but the public Atom/RSS feeds work.
Search RSS per term -> raw/L2_reddit_posts.jsonl (appended incrementally; resumable: done terms in raw/L2_reddit_done.txt).
Then: python scripts/L2_reddit_rss.py --csv   -> dedup to raw/L2_reddit_posts.csv
Rerun:  python scripts/L2_reddit_rss.py          (skips terms already done)
Polite: 5 s between requests (shared IP with other scrapers), 60 s back-off on 429, descriptive User-Agent.
"""
import requests, feedparser, time, json, csv, re, sys, os, html
from bs4 import BeautifulSoup

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, 'raw')
H = {'User-Agent': 'research-script/0.1 (DKS labor model study; contact palazzolojustin@gmail.com)'}
PJ = os.path.join(RAW, 'L2_reddit_posts.jsonl')
DONE = os.path.join(RAW, 'L2_reddit_done.txt')

# priority order; (sub, term, sort)
JOBS = []
P1 = ['built to win', 'new model', 'restructure', 'demoted', 'hours', 'payroll', 'lead', 'specialist', 'store manager',
      'ASM', 'operations lead', 'severance', 'team captain', 'captain', 'teammate', 'on field', 'off field',
      'department manager', 'layoff', 'laid off', 'pay cut', 'raise', 'budget', 'schedule', 'self checkout', 'pulse survey',
      'memo', 'new roles', 'eliminated', 'transition', 'position', 'role', 'pay', 'full time', 'salary', 'promotion',
      'understaffed', 'short staffed', 'labor', 'coverage', 'house of sport', 'field house', 'going going gone', 'golf galaxy',
      'merit', 'bonus', 'benefits', 'interview', 'district', 'manager', 'changes', 'new structure', 'quit', 'turnover',
      'sales lead', 'front end', 'cashier', 'BOPIS', 'ship from store', 'truck', 'inventory', 'AI', 'kronos', 'MyLocker',
      'play routines', 'persona', 'personas', 'footwear', 'apparel', 'hardlines', 'LOD', 'STL', 'fired', 'cuts', 'hourly', 'wage',
      'part time', 'promoted', 'leadership', 'store leadership', 'reorg', 'reorganization', 'new titles', 'job title',
      'demotion', 'step down', 'pay rate', '$15', '$16', '$17', '$18', 'minimum wage', 'hiring', 'seasonal', 'holiday']
CORE = ['built to win', 'BTW', 'restructure', 'restructuring', 'captain', 'specialist', 'severance', 'demoted', 'ASM',
        'pay cut', 'hours', 'payroll', 'lead', 'AA', 'key carrier', 'assessment', 'D-Day', 'store manager', 'benefits',
        'maternity', 'raise', 'pay', 'union', 'strike', 'pulse survey', 'schedule', 'seasonal', 'self checkout', 'legion',
        'house of sport', 'going going gone', 'golf galaxy', 'quit', 'layoff', 'eliminated', '38 hours', '32 hours', 'full time']
if os.environ.get('L2_FULL'):
    CORE = CORE + [t for t in P1 if t not in CORE]
for t in CORE:
    JOBS.append(('DicksSportingGoods', t, 'new'))
for t in ['restructure', 'captain', 'specialist', 'hours', 'payroll']:
    JOBS.append(('DicksSportingGoods', t, 'relevance'))
for s in ['retailhell', 'RetailManagement']:
    for t in ['dicks sporting goods', 'dicks restructure']:
        JOBS.append((s, t, 'new'))


def get(url):
    for i in range(4):
        try:
            r = requests.get(url, headers=H, timeout=30)
            if r.status_code == 429:
                print('429, sleeping', flush=True); time.sleep(60); continue
            return r
        except Exception:
            time.sleep(10)
    return None


def clean(htmltext):
    t = BeautifulSoup(html.unescape(htmltext or ''), 'html.parser').get_text(' ')
    t = re.sub(r'submitted by /u/\S+ \[link\] \[comments\]', '', t)
    return re.sub(r'\s+', ' ', t).strip()


def entries_to_rows(f, sub, term):
    out = []
    for e in f.entries:
        m = re.search(r'/comments/([a-z0-9]+)/', e.link)
        out.append({'id': m.group(1) if m else e.link, 'sub': sub, 'date': e.get('published', e.get('updated', '')),
                    'title': e.title, 'author': e.get('author', ''), 'link': e.link,
                    'text': clean(e.get('content', [{}])[0].get('value', '') if e.get('content') else e.get('summary', '')),
                    'term': term})
    return out


def main():
    done = set(open(DONE, encoding='utf-8').read().splitlines()) if os.path.exists(DONE) else set()
    feeds = [('DicksSportingGoods', 'feed:new', 'https://www.reddit.com/r/DicksSportingGoods/new/.rss?limit=100'),
             ('DicksSportingGoods', 'feed:top_year', 'https://www.reddit.com/r/DicksSportingGoods/top/.rss?t=year&limit=100'),
             ('DicksSportingGoods', 'feed:top_month', 'https://www.reddit.com/r/DicksSportingGoods/top/.rss?t=month&limit=100'),
             ('DicksSportingGoods', 'feed:top_all', 'https://www.reddit.com/r/DicksSportingGoods/top/.rss?t=all&limit=100'),
             ('DicksSportingGoods', 'feed:comments', 'https://www.reddit.com/r/DicksSportingGoods/comments/.rss?limit=100')]
    jobs = [(s, f'{t}', f'https://www.reddit.com/r/{s}/search.rss?q={requests.utils.quote(t)}&restrict_sr=1&sort={so}&t=all&limit=100', so) for s, t, so in JOBS]
    allj = [(s, k, u, 'feed') for s, k, u in feeds] + jobs
    with open(PJ, 'a', encoding='utf-8') as fh, open(DONE, 'a', encoding='utf-8') as dh:
        for s, t, u, so in allj:
            key = f'{s}|{t}|{so}'
            if key in done:
                continue
            r = get(u); time.sleep(5)
            if r is None or r.status_code != 200:
                print('FAIL', key, r.status_code if r is not None else None, flush=True); continue
            rows = entries_to_rows(feedparser.parse(r.text), s, t)
            for x in rows:
                fh.write(json.dumps(x, ensure_ascii=False) + '\n')
            fh.flush(); dh.write(key + '\n'); dh.flush()
            print(key, len(rows), flush=True)


def to_csv():
    posts = {}
    for line in open(PJ, encoding='utf-8'):
        p = json.loads(line)
        if p['id'] in posts:
            if p['term'] not in posts[p['id']]['term'].split('|'):
                posts[p['id']]['term'] += '|' + p['term']
        else:
            posts[p['id']] = p
    with open(os.path.join(RAW, 'L2_reddit_posts.csv'), 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=['id', 'sub', 'date', 'title', 'author', 'link', 'term', 'text'])
        w.writeheader()
        for p in sorted(posts.values(), key=lambda x: x['date'], reverse=True):
            w.writerow(p)
    print('unique posts', len(posts))


if __name__ == '__main__':
    if '--csv' in sys.argv:
        to_csv()
    else:
        main()
