"""H05: convert Apify get-dataset-items dumps (MCP tool-result .txt JSON files) into a flat review CSV.
Usage: python H05_extract_reviews.py <out_csv> <dump1.txt> [dump2.txt ...]
Appends (dedup on reviewId) to out_csv. Keeps: placeId, title, address, reviewsCount, review date, stars,
text length, owner-response flag, and the first 300 chars of the text (public review text, no reviewer names).
"""
import json, sys, csv, os

out = sys.argv[1]
rows = {}
if os.path.exists(out):
    with open(out, encoding='utf-8') as f:
        for r in csv.DictReader(f):
            rows[r['reviewId']] = r
places = {}
for fn in sys.argv[2:]:
    raw = open(fn, encoding='utf-8').read()
    d = json.loads(raw)
    if isinstance(d, list):  # MCP sometimes wraps as [{type:text,text:...}]
        d = json.loads(d[0]['text'])
    for it in d['items']:
        pid = it.get('placeId')
        places[pid] = (it.get('title'), it.get('address'), it.get('reviewsCount'))
        for rv in it.get('reviews') or []:
            rid = rv.get('reviewId')
            txt = (rv.get('text') or '')
            rows[rid] = {'reviewId': rid, 'placeId': pid, 'title': it.get('title'), 'address': it.get('address'),
                         'reviewsCount': it.get('reviewsCount'), 'date': (rv.get('publishedAtDate') or '')[:10],
                         'stars': rv.get('stars'), 'textlen': len(txt), 'owner_resp': int(bool(rv.get('responseFromOwnerText'))),
                         'text300': txt[:300].replace('\n', ' ')}
keys = ['reviewId', 'placeId', 'title', 'address', 'reviewsCount', 'date', 'stars', 'textlen', 'owner_resp', 'text300']
with open(out, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, keys); w.writeheader(); w.writerows(rows.values())
import collections
c = collections.Counter(r['address'] for r in rows.values())
for a, n in c.most_common():
    print(n, a)
print('total', len(rows))
