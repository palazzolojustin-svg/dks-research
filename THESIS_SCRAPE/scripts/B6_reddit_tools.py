"""B6: Reddit public JSON search in r/DicksSportingGoods (+ r/dickssportinggoods casing) for store-tech/labor tools.
Rerun: python B6_reddit_tools.py -> raw/B6_reddit_tools.jsonl and prints dated table.
"""
import requests, json, time, datetime, sys
H = {'User-Agent': 'python:dks-research-b6:v0.1 (by palazzolojustin@gmail.com)'}
TERMS = sys.argv[1:] or ['legion', 'legion app', 'kronos', 'workday schedule', 'rfid', 'stockit', 'zebra', 'self checkout', 'handheld',
         'scheduling app', 'labor hours', 'payroll hours', 'hours cut', 'theatro', 'zipline', 'axonify', 'ship from store', 'BOPIS']
OUT = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\B6_reddit_tools.jsonl'
f = open(OUT, 'a', encoding='utf-8')
for t in TERMS:
    after = None; n = 0
    for page in range(4):
        u = f'https://www.reddit.com/r/DicksSportingGoods/search.json?q={requests.utils.quote(t)}&restrict_sr=1&sort=new&limit=100&t=all'
        if after: u += '&after=' + after
        try:
            r = requests.get(u, headers=H, timeout=30)
            if r.status_code != 200: print('HTTP', r.status_code, t); time.sleep(5); break
            d = r.json()['data']
        except Exception as e:
            print('ERR', t, e); break
        for c in d['children']:
            p = c['data']; n += 1
            rec = {'term': t, 'date': datetime.datetime.utcfromtimestamp(p['created_utc']).strftime('%Y-%m-%d'), 'title': p['title'],
                   'text': (p.get('selftext') or '')[:1500], 'score': p['score'], 'num_comments': p['num_comments'], 'url': 'https://www.reddit.com' + p['permalink']}
            f.write(json.dumps(rec) + '\n')
        after = d.get('after'); time.sleep(2.5)
        if not after: break
    print(t, n); f.flush()
