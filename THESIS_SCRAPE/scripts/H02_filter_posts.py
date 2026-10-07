"""H02: filter saved WP posts to DICK'S-related ones and print opening/size/relocation snippets.
Rerun: python H02_filter_posts.py <posts.json> [title_regex]
"""
import sys, json, re
posts = json.load(open(sys.argv[1], encoding='utf8'))
tre = re.compile(sys.argv[2] if len(sys.argv) > 2 else r"(?i)dick|house of sport|field house")
KEY = re.compile(r"(?i)(open[a-z]*|slated|expected|anticipat|target|square[- ]f|sq\.? ?ft|relocat|current store|existing|clos[a-z]+|lease|permit|\$\d)")
for p in sorted(posts, key=lambda x: x['date'], reverse=True):
    titleonly = len(sys.argv) > 3 and sys.argv[3] == 'titleonly'
    if titleonly and not tre.search(p['title']):
        continue
    if not tre.search(p['title']) and not re.search(r"(?i)house of sport", p['text']):
        continue
    if not re.search(r"(?i)dick", p['text']):
        continue
    print('=' * 5, p['date'][:10], '|', p['title'], '|', p['link'])
    sents = re.split(r'(?<=[.!?])\s+', p['text'])
    out = [s for s in sents if KEY.search(s) and re.search(r"(?i)dick|house of sport|store|20\d\d", s)]
    for s in out[:10]:
        print('   -', s[:400])
