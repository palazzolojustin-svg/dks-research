"""H06: analyze Workday postings + details. Rerun after H06_workday_scrape.py and H06_workday_details.py.
Prints: per-format staffing intensity, posting-date series (startDate) by location type, req sequence vs date,
HoS-specific roles, pay ranges by format, new-store/pre-opening reqs, construction/real-estate corporate reqs.
Writes raw/H06_store_level_<date>.csv
"""
import pandas as pd, json, glob, os, re
pd.set_option('display.max_rows', 500); pd.set_option('display.width', 250); pd.set_option('display.max_colwidth', 140)
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'raw')
f = sorted(glob.glob(os.path.join(RAW, 'H06_workday_details_*.jsonl')))[-1]
d = pd.DataFrame([json.loads(l) for l in open(f, encoding='utf-8')])
d['startDate'] = pd.to_datetime(d.startDate, errors='coerce')
d['seq'] = d.req.str.extract(r'(\d{9})')[0].astype(float)
d['yr'] = d.seq // 100000
d['n'] = d.seq % 100000
d['store'] = d.location.str.extract(r'Store(\d{4})')[0].astype(float)
d['pay'] = d.desc.str.extract(r'(\$\s?\d[\d,.]*\s?(?:-|–|to)\s?\$\s?\d[\d,.]*)')[0]
d['pay_lo'] = d.pay.str.extract(r'\$\s?([\d,.]+)')[0].str.replace(',', '').astype(float)
print('rows', len(d), 'with startDate', d.startDate.notna().sum())
print(d.groupby('location_type').startDate.describe())
# req seq vs startDate (2026 numbering)
s = d[d.yr == 2026].groupby(d.startDate.dt.to_period('M')).n.agg(['min', 'median', 'max', 'size'])
print('2026 req seq by posting month\n', s)
s5 = d[d.yr == 2025].groupby(d.startDate.dt.to_period('M')).n.agg(['min', 'median', 'max', 'size'])
print('2025 req seq by posting month\n', s5)
# flags
for kw in ['new store', 'grand opening', 'opening', 'pre-opening', 'preopening', 'set up', 'setup', 'temporary', 'relocat', 'climb', 'HitTrax', 'TrackMan', 'turf', 'ice rink', 'experience']:
    m = d.desc.str.contains(kw, case=False, na=False)
    print(f'{kw:15s}', m.sum(), d[m].location_type.value_counts().to_dict())
d.to_pickle(os.path.join(RAW, '..', 'raw', 'H06_details.pkl'))
