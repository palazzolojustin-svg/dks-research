"""L2: monthly counts of r/DicksSportingGoods posts (deduped) mentioning store-labor topics, from raw/L2_reddit_posts.jsonl.
Caveat: Reddit search RSS returns at most ~100 newest posts per term, so older months are under-sampled for
high-volume terms; counts are a lower bound and best read as 2026 intensity, not a clean 2025-vs-2026 rate.
Also builds raw/L2_reddit_posts.csv (dedup). Rerun: python scripts/L2_monthly_counts.py
"""
import json, re, os, collections, csv
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, 'raw')
posts = {}
for l in open(os.path.join(RAW, 'L2_reddit_posts.jsonl'), encoding='utf-8'):
    p = json.loads(l)
    if p['id'] not in posts and '/comments/' in p['link'] and p['link'].count('/') <= 9:
        posts[p['id']] = p
CATS = {
 'restructure/BTW': r'built to win|\bBTW\b|restructur|reorgani|new model|new structure|D-?Day|decision day',
 'demotion/severance/pay cut': r'demot|severance|pay cut|cut my pay|less pay|lateral',
 'new roles (captain/specialist)': r'captain|specialist|advisor',
 'hours/payroll': r'\bhours\b|payroll|short.?staff|understaff|schedule',
 'pay/raise': r'\braise\b|\bpay\b|wage|salary|\$\d',
 'union/strike': r'union|strike',
}
months = collections.defaultdict(lambda: collections.Counter())
for p in posts.values():
    m = p['date'][:7]
    txt = p['title'] + ' ' + p['text']
    months[m]['all_collected'] += 1
    for c, rx in CATS.items():
        if re.search(rx, txt, re.I):
            months[m][c] += 1
keys = ['all_collected'] + list(CATS)
with open(os.path.join(RAW, 'L2_reddit_monthly_counts.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['month'] + keys)
    for m in sorted(months):
        if m >= '2025-01':
            w.writerow([m] + [months[m][k] for k in keys])
            print(m, [months[m][k] for k in keys])
with open(os.path.join(RAW, 'L2_reddit_posts.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['id', 'sub', 'date', 'title', 'author', 'link', 'term', 'text'])
    w.writeheader()
    for p in sorted(posts.values(), key=lambda x: x['date'], reverse=True):
        w.writerow({k: p.get(k, '') for k in w.fieldnames})
print('unique posts', len(posts))
