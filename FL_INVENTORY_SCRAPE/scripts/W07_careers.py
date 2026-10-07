import json, time, requests, sys, os
out = '/home/user/dks-research/FL_INVENTORY_SCRAPE/raw/W07/careers_all.json'
jobs = []
page = 1
while True:
    r = requests.get('https://careers.footlocker.com/api/jobs', params={'page': page, 'limit': 100}, timeout=60)
    d = r.json()
    js = d.get('jobs', [])
    if not js: break
    jobs += [j['data'] for j in js]
    print(page, len(jobs), d.get('totalCount'), flush=True)
    page += 1
    time.sleep(0.7)
json.dump(jobs, open(out, 'w'))
