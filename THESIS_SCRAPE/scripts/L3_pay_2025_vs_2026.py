"""L3: compare posted pay bands, pre-Built-to-Win (archived Workday CXS JSON, mostly 2025) vs live 2026-10-07 census.
Inputs: raw/L3_archived_cxs.jsonl (L3_fetch_archived_cxs.py), raw/H06_details.pkl (wave-1 H06 live census).
Rerun: python L3_pay_2025_vs_2026.py -> raw/L3_pay_pre_vs_post.csv, raw/L3_archived_cxs_table.csv
Method: map titles to role families; for each state compare the modal posted floor/ceiling per family, pre vs post.
"""
import pandas as pd, json, os, re
pd.set_option('display.width', 250); pd.set_option('display.max_rows', 500); pd.set_option('display.max_colwidth', 70)
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'raw')


def num(x):
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return None
    x = str(x).replace(',', '').rstrip('.')
    try:
        return float(x)
    except ValueError:
        return None


def fam(t, loc=''):
    t = (t or '').lower()
    if 'seasonal' in t: return 'Seasonal'
    if 'team captain' in t: return 'Team Captain (new)'
    if t.startswith('specialist'): return 'Specialist (new)'
    if t.startswith('teammate'): return 'Teammate (new)'
    if t.startswith('advisor'): return 'Advisor (new)'
    if 'assistant store manager' in t or 'asm' in t.split(): return 'ASM'
    if 'store manager' in t or 'store director' in t: return 'Store Mgr'
    if 'department manager' in t or 'dept manager' in t: return 'Dept Mgr'
    if 'golf professional' in t: return 'Golf Pro'
    if re.search(r'\blead\b|leader|key holder|keyholder|supervisor', t): return 'Hourly Lead (old)'
    if 'specialist' in t or 'fitter' in t or 'technician' in t or 'tech' in t.split(): return 'Hourly specialist/tech (old)'
    if 'associate' in t or 'cashier' in t or 'assoicate' in t or re.search(r'^retail ', t) or 'ambassador' in t or 'representative' in t: return 'Hourly associate (old)'
    return 'Other'


rows = []
for l in open(os.path.join(RAW, 'L3_archived_cxs.jsonl'), encoding='utf-8'):
    r = json.loads(l)
    if not r.get('title'):
        continue
    loc = r.get('location') or ''
    st = re.search(r'\b([A-Z]{2})$', loc.strip())
    rows.append({'src': 'pre', 'cap': r['timestamp'][:8], 'title': r['title'], 'location': loc, 'store': bool(re.match(r'Store\d{4}', loc)),
                 'state': st.group(1) if st else None, 'startDate': r.get('startDate'), 'timeType': r.get('timeType'),
                 'lo': num(r.get('pay_lo')), 'hi': num(r.get('pay_hi')), 'req': r.get('req')})
# add old careers-site (Radancy) archived job pages, if fetched (L3_fetch_radancy_pay.py)
rp = os.path.join(RAW, 'L3_radancy_pay.jsonl')
if os.path.exists(rp):
    for l in open(rp, encoding='utf-8'):
        r = json.loads(l)
        pt = (r.get('page_title') or '').replace('&#039;', "'")
        m = re.match(r'(.+?) in (.+?), ([A-Z]{2}) \|', pt)
        if not m:
            continue
        rows.append({'src': 'pre', 'cap': r['timestamp'][:8], 'title': m.group(1), 'location': f'{m.group(2)} {m.group(3)}', 'store': True,
                     'state': m.group(3), 'startDate': None, 'timeType': r.get('timeType'), 'lo': num(r.get('lo')), 'hi': num(r.get('hi')),
                     'req': r['req']})
a = pd.DataFrame(rows)
a['startDate'] = a.startDate.fillna(a.cap.str[:4] + '-' + a.cap.str[4:6] + '-xx')
a['req'] = a.req.astype(str).str.extract(r'(20\d{7})')[0].fillna(a.req.astype(str))
a['req_yr'] = a.req.str[:4]
# HoS / Golf Galaxy titles are outside Built to Win; drop from the pre sample for like-for-like DSG
a = a[~a.title.str.contains('House of Sport|Golf Galaxy|GGXY|Public Lands', case=False, na=False)]
# 2026 reqs with seq > 8748 were created after the Jun-15 cutover: exclude from "pre"
a = a[~((a.req_yr == '2026') & (pd.to_numeric(a.req.str[4:], errors='coerce') > 8748))]
a = a.drop_duplicates('req')
a['fam'] = a.title.apply(fam)
a.drop_duplicates('req').to_csv(os.path.join(RAW, 'L3_archived_cxs_table.csv'), index=False)
a = a.drop_duplicates('req')
print('archived records', len(a), 'store', a.store.sum(), 'with pay', a.lo.notna().sum())
print(a.startDate.str[:7].value_counts().sort_index().to_string())
print(a[a.store].fam.value_counts())

d = pd.read_pickle(os.path.join(RAW, 'H06_details.pkl'))
m = d.desc.str.extract(r'Targeted Pay Range:\s*\$([\d,]+(?:\.\d+)?)\s*-\s*\$([\d,]+(?:\.\d+)?)')
b = pd.DataFrame({'src': 'post', 'title': d.title, 'location': d.location, 'state': d.state, 'startDate': d.startDate.astype(str),
                  'lo': m[0].str.replace(',', '').astype(float), 'hi': m[1].str.replace(',', '').astype(float), 'location_type': d.location_type})
b['store'] = b.location.str.match(r'Store\d{4}', na=False)
b['fam'] = b.title.apply(fam)
# exclude HoS / Golf Galaxy from post for like-for-like DSG comparison when possible
b_dsg = b[b.location_type.isin(["DICK'S Sporting Goods", "DICK'S Sporting Goods (DSG + GG)", 'Going Going Gone!'])]
pa = a[a.store & a.lo.notna()]
pb = b_dsg[b_dsg.store & b_dsg.lo.notna()]


def mode(s):
    return s.mode().iloc[0] if len(s.mode()) else None


ga = pa.groupby(['state', 'fam']).agg(n_pre=('lo', 'size'), lo_pre=('lo', mode), hi_pre=('hi', mode), dates_pre=('startDate', lambda s: f"{min(s)[:7]}..{max(s)[:7]}"))
gb = pb.groupby(['state', 'fam']).agg(n_post=('lo', 'size'), lo_post=('lo', mode), hi_post=('hi', mode))
print('PRE store pay by state x family\n', ga.to_string())
print('POST (DSG/GGG only) store pay by state x family\n', gb.to_string())
# like-for-like: hourly associate (old) pre  vs Teammate (new) post; Hourly Lead (old) pre vs Specialist/Team Captain post
pairs = [('Hourly associate (old)', 'Teammate (new)'), ('Hourly associate (old)', 'Seasonal'), ('Hourly Lead (old)', 'Specialist (new)'),
         ('Hourly Lead (old)', 'Team Captain (new)'), ('ASM', 'ASM'), ('Hourly specialist/tech (old)', 'Specialist (new)')]
out = []
for pf, qf in pairs:
    x = ga.xs(pf, level='fam') if pf in ga.index.get_level_values('fam') else pd.DataFrame()
    y = gb.xs(qf, level='fam') if qf in gb.index.get_level_values('fam') else pd.DataFrame()
    j = x.join(y, how='inner')
    for stt, r in j.iterrows():
        out.append([pf, qf, stt, r.n_pre, r.lo_pre, r.hi_pre, r.dates_pre, r.n_post, r.lo_post, r.hi_post])
o = pd.DataFrame(out, columns=['pre_family', 'post_family', 'state', 'n_pre', 'lo_pre', 'hi_pre', 'pre_dates', 'n_post', 'lo_post', 'hi_post'])
o['lo_chg_pct'] = (o.lo_post / o.lo_pre - 1) * 100
o['mid_chg_pct'] = ((o.lo_post + o.hi_post) / (o.lo_pre + o.hi_pre) - 1) * 100
o.to_csv(os.path.join(RAW, 'L3_pay_pre_vs_post.csv'), index=False)
print(o.round(1).to_string())
print(o.groupby(['pre_family', 'post_family'])[['lo_chg_pct', 'mid_chg_pct']].agg(['median', 'mean', 'count']).round(1))
# pre split by requisition year: did bands move at the Jan-2026 merit cycle (before Built to Win)?
pa2 = pa.copy()
g2 = pa2[pa2.fam.isin(['Hourly associate (old)', 'Hourly Lead (old)', 'ASM'])].groupby(['fam', 'state', 'req_yr']).agg(n=('lo', 'size'), lo=('lo', mode), hi=('hi', mode)).unstack('req_yr')
print('PRE by req year\n', g2.to_string())
print('pre sample sizes: total', len(a), 'store w/ pay', len(pa), 'by req_yr', pa.req_yr.value_counts().to_dict())
