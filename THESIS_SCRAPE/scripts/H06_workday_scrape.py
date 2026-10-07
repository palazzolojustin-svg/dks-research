"""H06: scrape DICK'S Sporting Goods public Workday job board (the JSON endpoint the careers page itself calls).

Endpoint: POST https://dickssportinggoods.wd1.myworkdayjobs.com/wday/cxs/dickssportinggoods/DSG/jobs
Rerun:  python H06_workday_scrape.py
Outputs (THESIS_SCRAPE/raw/):
  H06_workday_facets_<date>.json         facet counts overall and per Location Type
  H06_workday_loc_by_type_<date>.csv      location (store) x location type x posting count
  H06_workday_postings_<date>.csv         every posting (title, location, postedOn, req id, path)
No login, no form submission; public read-only API, polite 0.4s delay.
"""
import requests, json, time, csv, datetime, os, sys

BASE = 'https://dickssportinggoods.wd1.myworkdayjobs.com/wday/cxs/dickssportinggoods/DSG/jobs'
H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36',
     'Content-Type': 'application/json', 'Accept': 'application/json'}
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'raw')
D = datetime.date.today().isoformat()
LT = 'CF_-_Job_Posting_Location_Type__LRV__Extended'
s = requests.Session()


def post(facets, offset=0, text=''):
    for a in range(5):
        try:
            r = s.post(BASE, headers=H, json={"appliedFacets": facets, "limit": 20, "offset": offset, "searchText": text}, timeout=40)
            if r.status_code == 200:
                return r.json()
        except Exception as e:
            print('err', e)
        time.sleep(2 + 3 * a)
    raise RuntimeError('failed')


def facet_map(d):
    out = {}
    for f in d.get('facets', []):
        if 'values' in f and f['values'] and 'values' in f['values'][0]:
            for sub in f['values']:
                out[sub['facetParameter']] = sub['values']
        else:
            out[f['facetParameter']] = f.get('values', [])
    return out


def main():
    d0 = post({})
    fm = facet_map(d0)
    facets_dump = {'all': fm}
    loc_rows = []
    for v in fm[LT]:
        d = post({LT: [v['id']]})
        f = facet_map(d)
        facets_dump[v['descriptor']] = f
        for loc in f.get('locations', []):
            loc_rows.append([v['descriptor'], loc['descriptor'], loc['count'], loc['id']])
        time.sleep(0.4)
    json.dump(facets_dump, open(os.path.join(RAW, f'H06_workday_facets_{D}.json'), 'w'), indent=1)
    with open(os.path.join(RAW, f'H06_workday_loc_by_type_{D}.csv'), 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh); w.writerow(['location_type', 'location', 'count', 'loc_id']); w.writerows(loc_rows)
    # enumerate postings per location type x state (each slice < 2000)
    rows = {}
    states = fm['locationRegionStateProvince']
    for v in fm[LT]:
        slices = [None] if v['count'] < 1900 else [st['id'] for st in states]
        for st in slices:
            fac = {LT: [v['id']]}
            if st:
                fac['locationRegionStateProvince'] = [st]
            off = 0
            total = None
            while True:
                d = post(fac, off)
                if total is None:
                    total = d.get('total', 0)  # Workday returns total only on the first page
                jp = d.get('jobPostings', [])
                for j in jp:
                    key = j.get('externalPath')
                    rows[key] = [v['descriptor'], j.get('title'), j.get('locationsText'), j.get('postedOn'),
                                 (j.get('bulletFields') or [''])[0], key]
                off += 20
                if off >= total or not jp:
                    break
                time.sleep(0.4)
        print(v['descriptor'], len(rows)); sys.stdout.flush()
    with open(os.path.join(RAW, f'H06_workday_postings_{D}.csv'), 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh); w.writerow(['location_type', 'title', 'location', 'postedOn', 'req_id', 'path']); w.writerows(rows.values())
    print('done', len(rows))


if __name__ == '__main__':
    main()
