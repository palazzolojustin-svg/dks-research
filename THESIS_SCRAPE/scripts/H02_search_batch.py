"""H02: run a batch of Bing-RSS searches from a text file (one query per line) and save results.
Rerun: python H02_search_batch.py queries.txt out.json
"""
import sys, json, time
from H02_search import bing_rss, ddg

qs = [l.strip() for l in open(sys.argv[1], encoding='utf8') if l.strip()]
out = {}
for q in qs:
    try:
        res = bing_rss(q, 30) or ddg(q) or []
    except Exception as e:
        res = []
    out[q] = res
    print('##', q, len(res))
    for t, u, d, s in res[:30]:
        print('  ', t[:100], '|', u, '|', d[:16], '|', s[:220].replace('\n', ' '))
    time.sleep(1.5)
json.dump(out, open(sys.argv[2], 'w', encoding='utf8'), indent=1)
