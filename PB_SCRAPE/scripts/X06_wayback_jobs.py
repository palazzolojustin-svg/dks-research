"""X06: Wayback Machine CDX history of DKS job-posting URLs (historical hiring baseline).

Rerun:  python X06_wayback_jobs.py
Output: PB_SCRAPE/raw/X06_wayback_joburls.csv  (one row per unique job URL: first capture date, title slug, req id)

Method: the Wayback CDX API lists every archived URL under a prefix. Workday job URLs embed the job title and
requisition number (e.g. /DSG/job/Customer-Support-Center/Vertical-Brand-Merchant_202636890), and the
www.dickssportinggoods.jobs front end embeds slug + req id (/job/<slug>/<city>/<reqid>/). So the archive gives a
dated sample of historical postings even though the old postings are gone. Captures are a SAMPLE (whatever the
crawler happened to hit), so compare SHARES (vertical-brand titles / all corporate titles), not raw counts.
"""
import requests, csv, re, os, time, json

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'raw')
PREFIXES = [
    'dickssportinggoods.wd1.myworkdayjobs.com/DSG/job/',
    'dickssportinggoods.wd1.myworkdayjobs.com/en-US/DSG/job/',
    'dickssportinggoods.wd1.myworkdayjobs.com/dsg/job/',
    'www.dickssportinggoods.jobs/job/',
    'dickssportinggoods.jobs/job/',
]
H = {'User-Agent': 'Mozilla/5.0 research script (contact: none)'}


def cdx(prefix):
    rows, resume = [], None
    while True:
        params = {'url': prefix, 'matchType': 'prefix', 'output': 'json', 'fl': 'timestamp,original,statuscode',
                  'collapse': 'urlkey', 'limit': '15000', 'showResumeKey': 'true'}
        if resume:
            params['resumeKey'] = resume
        for i in range(5):
            try:
                r = requests.get('https://web.archive.org/cdx/search/cdx', params=params, headers=H, timeout=120)
                if r.status_code == 200:
                    break
            except Exception:
                pass
            time.sleep(5 * (i + 1))
        data = r.json() if r.text.strip() else []
        if not data:
            break
        resume = None
        body = data[1:]
        if len(body) >= 2 and body[-2] == []:
            resume = body[-1][0]
            body = body[:-2]
        rows += body
        if not resume:
            break
    return rows


def main():
    allrows = []
    for p in PREFIXES:
        rs = cdx(p)
        print(p, len(rs))
        for ts, orig, sc in rs:
            m = re.search(r'_(\d{9,11}(?:-\d)?)', orig) or re.search(r'/(\d{9,11})/?', orig)
            req = m.group(1) if m else ''
            if 'myworkdayjobs' in orig:
                slug = orig.split('/job/')[-1].split('/')[-1].split('?')[0]
                slug = re.sub(r'_\d{9,11}(-\d)?$', '', slug)
                loc = orig.split('/job/')[-1].split('/')[0]
            else:
                parts = orig.split('/job/')[-1].split('/')
                slug, loc = (parts[0], parts[1] if len(parts) > 1 else '')
            allrows.append({'first_capture': ts[:8], 'req': req, 'title_slug': slug, 'loc': loc, 'status': sc, 'url': orig})
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, 'X06_wayback_joburls.csv'), 'w', newline='', encoding='utf8') as f:
        w = csv.DictWriter(f, fieldnames=list(allrows[0].keys()))
        w.writeheader()
        w.writerows(allrows)
    print('total', len(allrows))


if __name__ == '__main__':
    main()
