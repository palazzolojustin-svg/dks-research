"""H06: time series of DKS open job postings from Wayback Machine snapshots of https://www.dickssportinggoods.jobs/jobs/
(and brand pages). Extracts the 'N Results found in all locations' total, brand-filter counts if present, and the
requisition IDs visible on the page (req id = YYYY + sequence, so max seq at a date approximates requisitions opened YTD).
Rerun: python H06_wayback_jobs_series.py  -> THESIS_SCRAPE/raw/H06_wayback_jobs_series.csv
"""
import requests, re, time, csv, os
H = {'User-Agent': 'Mozilla/5.0 research (DKS thesis; contact via archive.org norms)'}
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'raw')
import sys
TARGETS = sys.argv[1:] or ['dickssportinggoods.jobs/jobs/', 'dickssportinggoods.jobs/jobs/brand/House-of-Sport/', 'dickssportinggoods.jobs/house-of-sport',
           'dickssportinggoods.jobs/jobs/brand/Field-House/']


def cdx(url):
    for a in range(4):
        try:
            r = requests.get('http://web.archive.org/cdx/search/cdx', params={'url': url, 'output': 'json', 'fl': 'timestamp,original,statuscode',
                             'filter': 'statuscode:200', 'collapse': 'timestamp:8', 'from': '2023'}, headers=H, timeout=120)
            return r.json()[1:]
        except Exception as e:
            print('cdx err', url, e); time.sleep(10)
    return []


rows = []
for tgt in TARGETS:
    snaps = cdx(tgt)
    print(tgt, len(snaps), flush=True)
    for ts, orig, sc in snaps:
        u = f'http://web.archive.org/web/{ts}id_/{orig}'
        txt = None
        for a in range(3):
            try:
                r = requests.get(u, headers=H, timeout=120)
                if r.status_code == 200:
                    txt = r.text; break
            except Exception as e:
                pass
            time.sleep(5)
        if not txt:
            rows.append([tgt, ts, '', '', '', '', 'fetch_fail']); continue
        m = re.search(r'id="totresultsspan">\s*([\d,]+)', txt) or re.search(r'([\d,]+)\s+Results found', txt)
        total = m.group(1).replace(',', '') if m else ''
        reqs = [int(x) for x in re.findall(r'/job/[^"\s]+/(\d{9})/', txt)]
        brand = {}
        for b in ['House of Sport', 'Field House', "DICK'S Sporting Goods", 'Golf Galaxy', 'Public Lands', 'Going Going Gone!', 'Corporate', 'Warehouse']:
            mm = re.search(re.escape(b).replace("'", "(?:'|&#039;|&#8217;|’)") + r'\s*(?:<[^>]+>\s*)*\(?\s*([\d,]+)\s*\)?', txt)
            if mm:
                brand[b] = mm.group(1)
        yr_max = {}
        for q in reqs:
            y = q // 100000
            yr_max[y] = max(yr_max.get(y, 0), q % 100000)
        rows.append([tgt, ts, total, len(reqs), ';'.join(f'{k}:{v}' for k, v in sorted(yr_max.items())), ';'.join(f'{k}={v}' for k, v in brand.items()), ''])
        print(rows[-1], flush=True)
        time.sleep(1.5)
with open(os.path.join(RAW, 'H06_wayback_jobs_series.csv'), 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh); w.writerow(['target', 'timestamp', 'total_results', 'n_reqs_on_page', 'max_seq_by_year', 'brand_counts', 'note']); w.writerows(rows)
print('done')
