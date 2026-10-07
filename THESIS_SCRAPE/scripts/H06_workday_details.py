"""H06: fetch job-detail JSON for every posting in the latest H06_workday_postings_<date>.csv.

Endpoint (public, the page itself calls it): GET https://dickssportinggoods.wd1.myworkdayjobs.com/wday/cxs/dickssportinggoods/DSG<externalPath>
Rerun: python H06_workday_details.py   (run H06_workday_scrape.py first)
Output: THESIS_SCRAPE/raw/H06_workday_details_<date>.jsonl  (req id, startDate = actual posting date, timeType, location,
        pay text, flags for 'new store'/'opening'/'grand opening', plain-text description)
"""
import requests, json, time, csv, glob, os, re, datetime, html

RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'raw')
BASE = 'https://dickssportinggoods.wd1.myworkdayjobs.com/wday/cxs/dickssportinggoods/DSG'
H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36', 'Accept': 'application/json'}
D = datetime.date.today().isoformat()
src = sorted(glob.glob(os.path.join(RAW, 'H06_workday_postings_*.csv')))[-1]
out = os.path.join(RAW, f'H06_workday_details_{D}.jsonl')
done = set()
if os.path.exists(out):
    for l in open(out, encoding='utf-8'):
        try:
            done.add(json.loads(l)['path'])
        except Exception:
            pass
s = requests.Session()
rows = list(csv.DictReader(open(src, encoding='utf-8')))
with open(out, 'a', encoding='utf-8') as fh:
    for i, r in enumerate(rows):
        if r['path'] in done:
            continue
        rec = {'path': r['path'], 'location_type': r['location_type'], 'title': r['title'], 'location': r['location']}
        for a in range(4):
            try:
                x = s.get(BASE + r['path'], headers=H, timeout=40)
                if x.status_code == 200:
                    j = x.json().get('jobPostingInfo', {})
                    desc = html.unescape(re.sub(r'<[^>]+>', ' ', j.get('jobDescription', '') or ''))
                    desc = re.sub(r'\s+', ' ', desc)
                    rec.update({'req': j.get('jobReqId'), 'startDate': j.get('startDate'), 'timeType': j.get('timeType'),
                                'remote': j.get('remoteType'), 'country': (j.get('country') or {}).get('descriptor'),
                                'additionalLocations': j.get('additionalLocations'), 'desc': desc})
                    break
                rec['status'] = x.status_code
                if x.status_code == 404:
                    break
            except Exception as e:
                rec['err'] = str(e)
            time.sleep(2 + 2 * a)
        fh.write(json.dumps(rec) + '\n')
        if i % 200 == 0:
            print(i, flush=True)
        time.sleep(0.25)
print('done')
