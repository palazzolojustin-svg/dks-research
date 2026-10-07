"""L2 helper: print full text of collected Reddit posts matching a regex (title+text), dedup by id.
Usage: python scripts/L2_show.py "<regex>" [maxchars] [term-filter-regex]
"""
import json, re, sys, os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rx = re.compile(sys.argv[1], re.I)
mx = int(sys.argv[2]) if len(sys.argv) > 2 else 3000
tf = re.compile(sys.argv[3], re.I) if len(sys.argv) > 3 else None
seen = set(); rows = []
for l in open(os.path.join(BASE, 'raw', 'L2_reddit_posts.jsonl'), encoding='utf-8'):
    p = json.loads(l)
    if p['id'] in seen: continue
    seen.add(p['id'])
    if tf and not tf.search(p['term']): continue
    if rx.search(p['title'] + ' ' + p['text']):
        rows.append(p)
rows.sort(key=lambda p: p['date'])
for p in rows:
    print(f"=== {p['date'][:10]} | {p['title']} | {p['link']} | {p['author']}")
    print(p['text'][:mx])
print('N =', len(rows))
