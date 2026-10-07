"""L4: EDGAR full-text search for retailer store labor-model / store-leadership restructuring language.
Rerun: python L4_edgar_fts.py  -> raw/L4_edgar_fts_hits.json (phrase -> list of hits) and prints filer counts.
Optional: python L4_edgar_fts.py "<phrase>" [forms] [startdt]
"""
import requests, json, time, sys, os
H = {'User-Agent': 'DKS research palazzolojustin@gmail.com', 'Accept': 'application/json'}
OUT = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\L4_edgar_fts_hits.json'
PHRASES = [
    'store operating model', 'store labor model', 'labor model', 'store leadership structure',
    'store leadership model', 'store staffing model', 'store team structure', 'field leadership structure',
    'store payroll', 'store labor hours', 'store management structure', 'store organizational structure',
    'new store operating model', 'store labor productivity', 'labor efficiencies', 'store labor efficiencies',
    'store leadership roles', 'assistant store manager', 'team lead', 'store-level management',
]
# retail SICs: 5200-5999 (retail trade). EDGAR FTS supports 'sics' param? Not reliably; filter by name later.

def fts(q, forms='10-K,10-Q,8-K', startdt='2017-01-01', enddt='2026-10-07', maxn=500):
    hits, start = [], 0
    while True:
        p = {'q': f'"{q}"', 'forms': forms, 'dateRange': 'custom', 'startdt': startdt, 'enddt': enddt, 'from': start}
        try:
            r = requests.get('https://efts.sec.gov/LATEST/search-index', params=p, headers=H, timeout=60)
            d = r.json()
        except Exception as e:
            print('ERR', q, e); break
        hh = d.get('hits', {}).get('hits', [])
        if not hh:
            break
        for x in hh:
            s = x['_source']
            hits.append(dict(name=(s.get('display_names') or ['?'])[0], form=s.get('form'), date=s.get('file_date'),
                             id=x['_id'], ciks=s.get('ciks'), sics=s.get('sics'), period=s.get('period_ending')))
        total = d['hits']['total']['value']
        start += len(hh)
        if start >= total or start >= maxn:
            break
        time.sleep(0.2)
    return hits

if __name__ == '__main__':
    res = json.load(open(OUT)) if os.path.exists(OUT) else {}
    phrases = [sys.argv[1]] if len(sys.argv) > 1 else PHRASES
    forms = sys.argv[2] if len(sys.argv) > 2 else '10-K,10-Q,8-K'
    startdt = sys.argv[3] if len(sys.argv) > 3 else '2017-01-01'
    for ph in phrases:
        h = fts(ph, forms, startdt)
        res[ph] = h
        retail = [x for x in h if x['sics'] and any(str(s).startswith(('52', '53', '54', '56', '57', '59')) for s in x['sics'])]
        print(f'== {ph}: {len(h)} hits, {len(retail)} retail-SIC')
        from collections import Counter
        c = Counter((x['name'][:45]) for x in retail)
        for nm, n in c.most_common(40):
            yrs = sorted(set(x['date'][:4] for x in retail if x['name'][:45] == nm))
            print(f'   {n:3d} {nm} {yrs}')
        json.dump(res, open(OUT, 'w'), indent=0)
        time.sleep(0.3)
