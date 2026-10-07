"""X14: list Wayback-captured files on DKS investor CDNs (q4cdn) to find factory-list / transparency-pledge / Purpose Playbook / Form SD versions.
Rerun: python X14_wayback_cdx.py [pattern ...]   (default patterns below). Output -> PB_SCRAPE/raw/X14_cdx_<n>.txt
"""
import requests, sys, time, json, os
PATS = sys.argv[1:] or [
    's23.q4cdn.com/425278312/files/*',
    's205.q4cdn.com/510074553/files/*',
    'investors.dicks.com/corporate-social-responsibility*',
    'investors.dicks.com/sustainability*',
]
OUT = os.path.join(os.path.dirname(__file__), '..', 'raw')
for i, p in enumerate(PATS):
    url = 'https://web.archive.org/cdx/search/cdx'
    params = {'url': p, 'output': 'json', 'fl': 'timestamp,original,mimetype,statuscode,length', 'collapse': 'urlkey', 'limit': '20000'}
    for attempt in range(3):
        try:
            r = requests.get(url, params=params, timeout=120)
            rows = r.json()
            break
        except Exception as e:
            print('retry', p, e); time.sleep(5); rows = []
    fn = os.path.join(OUT, f'X14_cdx_{i}.txt')
    with open(fn, 'w', encoding='utf-8') as f:
        for row in rows:
            f.write('\t'.join(row) + '\n')
    print(p, len(rows), '->', fn)
