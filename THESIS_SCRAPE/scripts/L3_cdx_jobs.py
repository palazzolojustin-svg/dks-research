"""L3: list every Wayback-archived DICK'S job-posting URL (pre- and post-Built-to-Win) via the CDX API.
Targets the old Radancy careers site (dickssportinggoods.jobs/job/<title>/<location>/<reqid>/) and Workday job URLs.
Rerun: python L3_cdx_jobs.py  -> THESIS_SCRAPE/raw/L3_cdx_jobs.csv (timestamp, original, statuscode, host)
Uses https://web.archive.org/cdx (port 80 is refused from this machine). Paged with page=N.
"""
import requests, time, csv, os
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'raw')
H = {'User-Agent': 'Mozilla/5.0 research (DKS thesis L3)'}
TARGETS = ['dickssportinggoods.jobs/job/', 'dickssportinggoods.wd1.myworkdayjobs.com/en-US/DSG/job/',
           'dickssportinggoods.wd1.myworkdayjobs.com/DSG/job/', 'dickssportinggoods.wd1.myworkdayjobs.com/wday/cxs/dickssportinggoods/DSG/job/',
           'dickssportinggoods.wd1.myworkdayjobs.com/en-US/DSG/details/']


def get(params):
    for a in range(10):
        try:
            r = requests.get('https://web.archive.org/cdx/search/cdx', params=params, headers=H, timeout=180)
            if r.status_code == 200:
                return r.text
            print('status', r.status_code)
        except Exception as e:
            print('err', str(e)[:100])
        time.sleep(min(60, 10 * (a + 1)))
    return None


import sys
OUT = sys.argv[1] if len(sys.argv) > 1 else 'L3_cdx_jobs.csv'
rows = []
for t in TARGETS:
    n = (get({'url': t, 'matchType': 'prefix', 'showNumPages': 'true'}) or '').strip()
    n = int(n) if n.isdigit() else 3
    for p in range(n):
        txt = get({'url': t, 'matchType': 'prefix', 'page': p, 'fl': 'timestamp,original,statuscode,mimetype'})
        if txt is None:
            print('FAILED page', t, p, flush=True)
            continue
        for l in txt.splitlines():
            parts = l.split(' ')
            if len(parts) >= 3:
                rows.append(parts[:4] + [t])
        print(t, 'page', p, 'of', n, len(rows), flush=True)
        time.sleep(3)
with open(os.path.join(RAW, OUT), 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh); w.writerow(['timestamp', 'original', 'statuscode', 'mimetype', 'target']); w.writerows(rows)
print('done', len(rows))
