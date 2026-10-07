"""L2 helper: print fetched threads (raw/L2_reddit_threads.jsonl). Usage: python scripts/L2_show_threads.py [id1,id2,...|all] [maxchars]"""
import json, sys, os, re
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
want = sys.argv[1] if len(sys.argv) > 1 else 'all'
mx = int(sys.argv[2]) if len(sys.argv) > 2 else 1500
ids = None if want == 'all' else set(want.split(','))
seen = set()
for line in open(os.path.join(BASE, 'raw', 'L2_reddit_threads.jsonl'), encoding='utf-8'):
    d = json.loads(line)
    if 'items' not in d: continue
    m = re.search(r'/comments/([a-z0-9]+)', d['url']); tid = m.group(1) if m else d['url']
    if (ids and tid not in ids) or tid in seen: continue
    seen.add(tid)
    print('#' * 10, tid, d['url'])
    for it in d['items']:
        print(f"- {it['date'][:10]} {it['author']}: {it['text'][:mx]}")
