"""X06: DICK'S Sporting Goods Workday job-feed scraper (vertical-brands hiring signal).

How to rerun (weekly):
    python X06_workday_jobs.py            # writes PB_SCRAPE/raw/X06_workday_<YYYYMMDD>.json and .csv

What it does:
  1. Uses the public Workday CXS endpoint the careers site itself calls:
       POST https://dickssportinggoods.wd1.myworkdayjobs.com/wday/cxs/dickssportinggoods/DSG/jobs
       body {"appliedFacets": {...}, "limit": 20, "offset": n, "searchText": "..."}
     (no login, no captcha; same JSON the browser receives)
  2. Pulls ALL non-store postings: location-type facet CSC/Corporate + Virtual, plus job-category facets
     Product Development / Merchandising / Planning-Allocations / Supply Chain / Advertising-Marketing,
     plus keyword searches (vertical brands, CALIA, VRST, DSG, Maxfli, product developer, technical designer,
     sourcing, designer, footwear, etc.).
  3. Fetches each posting's detail (GET .../DSG/job/<slug>) for full description, startDate, jobReqId.
  4. Flags vertical-brand-relevant postings by keyword and saves raw JSON + CSV.
Totals per facet are also stored (snapshot of the facet counts) so the series can be compared week to week.
Note: Workday caps "total" at 2000 for the unfiltered query; facet counts are not capped.
"""
import requests, json, time, re, csv, os, datetime, html

BASE = 'https://dickssportinggoods.wd1.myworkdayjobs.com/wday/cxs/dickssportinggoods/DSG'
H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36',
     'Accept': 'application/json', 'Content-Type': 'application/json', 'Accept-Language': 'en-US',
     'Origin': 'https://dickssportinggoods.wd1.myworkdayjobs.com', 'Referer': 'https://dickssportinggoods.wd1.myworkdayjobs.com/DSG'}
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'raw')

FACET_LOCTYPE = 'CF_-_Job_Posting_Location_Type__LRV__Extended'
FACET_CAT = 'CF_-_Job_Requisition_Job_Category__LRV__Extended'
KEYWORDS = ['vertical brands', 'vertical brand', 'CALIA', 'VRST', 'DSG brand', 'Maxfli', 'Walter Hagen', 'Alpine Design',
            'product developer', 'product development', 'technical designer', 'technical design', 'designer', 'sourcing',
            'footwear', 'apparel design', 'textile', 'merchant', 'buyer', 'quality assurance', 'fit', 'raw materials',
            'private brand', 'owned brand', 'brand marketing', 'golf']
VB_PAT = re.compile(r'vertical brand|calia|vrst|maxfli|walter hagen|alpine design|top[- ]flite|tommy armour|fitness gear|'
                    r'ethos|nishiki|quest|product develop|technical design|sourcing|textile|print and|designer|'
                    r'owned brand|private (label|brand)|raw material|fabric|trim|fit tech|costing|vendor compliance|'
                    r'factory|social compliance', re.I)


def post(body, tries=4):
    for i in range(tries):
        try:
            r = requests.post(BASE + '/jobs', headers=H, json=body, timeout=40)
            if r.status_code == 200:
                return r.json()
        except Exception as e:
            pass
        time.sleep(2 + 2 * i)
    raise RuntimeError('post failed %s' % body)


def get_facets():
    d = post({'appliedFacets': {}, 'limit': 1, 'offset': 0, 'searchText': ''})
    fac = {}
    for f in d.get('facets', []):
        vals = []
        for v in f.get('values', []):
            if 'values' in v:
                vals += v['values']
            else:
                vals.append(v)
        fac[f['facetParameter']] = {v['descriptor']: {'count': v['count'], 'id': v['id']} for v in vals}
    return fac


def list_all(applied, search=''):
    out, off = [], 0
    while True:
        d = post({'appliedFacets': applied, 'limit': 20, 'offset': off, 'searchText': search})
        jp = d.get('jobPostings', [])
        out += jp
        tot = d.get('total', 0)
        off += 20
        if not jp or off >= tot or off >= 2000:
            break
        time.sleep(0.4)
    return out


def detail(path):
    for i in range(4):
        try:
            r = requests.get(BASE + path, headers=H, timeout=40)
            if r.status_code == 200:
                return r.json()
        except Exception:
            pass
        time.sleep(2 + 2 * i)
    return {}


def strip(h):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', h or ''))).strip()


def main():
    today = datetime.date.today().strftime('%Y%m%d')
    fac = get_facets()
    postings = {}
    lt = fac.get(FACET_LOCTYPE, {})
    for name in ['CSC/Corporate', 'Virtual']:
        if name in lt:
            for j in list_all({FACET_LOCTYPE: [lt[name]['id']]}):
                postings[j['externalPath']] = j
    cat = fac.get(FACET_CAT, {})
    for name in ['Product Development', 'Merchandising', 'Planning/Allocations', 'Supply Chain Logistics',
                 'Advertising/Marketing', 'Students and Recent Grads', 'Technology', 'Legal', 'Finance', 'Operations',
                 'Risk/Compliance', 'Human Resources', 'Internal Audit', 'Facilities']:
        if name in cat:
            for j in list_all({FACET_CAT: [cat[name]['id']]}):
                postings[j['externalPath']] = j
    kw_hits = {}
    for kw in KEYWORDS:
        res = list_all({}, kw) if True else []
        kw_hits[kw] = len(res)
        for j in res:
            # keep only non-store postings from keyword searches
            if not j.get('locationsText', '').startswith('Store'):
                postings[j['externalPath']] = j
        time.sleep(0.4)
    rows = []
    for p, j in postings.items():
        d = detail(p)
        info = d.get('jobPostingInfo', {})
        desc = strip(info.get('jobDescription', ''))
        rows.append({
            'title': j.get('title'), 'location': j.get('locationsText'), 'postedOn': j.get('postedOn'),
            'startDate': info.get('startDate'), 'jobReqId': info.get('jobReqId'), 'timeType': info.get('timeType'),
            'url': 'https://dickssportinggoods.wd1.myworkdayjobs.com/DSG' + p,
            'vb_flag': bool(VB_PAT.search((j.get('title') or '') + ' ' + desc)),
            'vb_title_flag': bool(VB_PAT.search(j.get('title') or '')),
            'description': desc,
        })
        time.sleep(0.3)
    snap = {'date': today, 'facets': fac, 'keyword_hit_counts': kw_hits, 'postings': rows}
    os.makedirs(OUT, exist_ok=True)
    json.dump(snap, open(os.path.join(OUT, 'X06_workday_%s.json' % today), 'w', encoding='utf8'), indent=1)
    with open(os.path.join(OUT, 'X06_workday_%s.csv' % today), 'w', newline='', encoding='utf8') as f:
        w = csv.DictWriter(f, fieldnames=[k for k in rows[0] if k != 'description'] + ['description'])
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print('postings', len(rows), 'vb_flag', sum(r['vb_flag'] for r in rows), 'vb_title', sum(r['vb_title_flag'] for r in rows))
    print('keyword totals', kw_hits)


if __name__ == '__main__':
    main()
