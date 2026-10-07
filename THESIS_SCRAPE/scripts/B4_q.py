"""B4 helper: quick Bing News RSS look-up. Usage: python B4_q.py <queries.txt> [n]  (prints date|title|link|desc)"""
import sys
from B4_bing import bing
n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
for q in [l.strip() for l in open(sys.argv[1], encoding='utf8') if l.strip()]:
    try:
        c, it = bing(q)
    except Exception as e:
        print('##', q, 'ERR', e); continue
    print('##', q, c, len(it))
    for i in it[:n]:
        print('  ', i['date'][5:16], '|', i['title'][:110], '|', i['link'][:140])
        print('       ', i['desc'][:200].replace('\n', ' '))
