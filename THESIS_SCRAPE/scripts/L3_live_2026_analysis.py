"""L3: analyse the live 2026-10-07 Workday census (from wave-1 H06 raw/H06_details.pkl) for thesis #2.
- title families (new Built-to-Win architecture vs legacy titles) by location type
- req-id sequence windows: which titles were created in the Jun-Jul 2026 requisition spike
- posted pay ranges (pay-transparency states) by title family and state
Rerun: python L3_live_2026_analysis.py -> raw/L3_live2026_pay_by_title_state.csv, raw/L3_live2026_family_by_type.csv
"""
import pandas as pd, re, os
pd.set_option('display.width', 250); pd.set_option('display.max_rows', 400); pd.set_option('display.max_colwidth', 80)
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'raw')
d = pd.read_pickle(os.path.join(RAW, 'H06_details.pkl'))
m = d.desc.str.extract(r'Targeted Pay Range:\s*\$([\d,]+(?:\.\d+)?)\s*-\s*\$([\d,]+(?:\.\d+)?)')
d['lo'] = m[0].str.replace(',', '').astype(float)
d['hi'] = m[1].str.replace(',', '').astype(float)
d['hourly'] = d.lo < 200


def fam(t):
    t = (t or '').lower()
    if 'seasonal' in t: return 'Seasonal'
    if 'team captain' in t: return 'NEW Team Captain'
    if t.startswith('specialist'): return 'NEW Specialist'
    if t.startswith('teammate'): return 'NEW Teammate'
    if t.startswith('advisor'): return 'NEW Advisor'
    if 'assistant store manager' in t: return 'ASM'
    if 'store manager' in t or 'store director' in t: return 'Store Mgr/Director'
    if 'lead' in t or 'leader' in t or 'key holder' in t: return 'OLD Lead'
    if 'golf professional' in t: return 'Golf Pro'
    if t.startswith('retail') or 'associate' in t or 'cashier' in t or 'technician' in t: return 'OLD Associate/Tech'
    return 'Other'


d['fam'] = d.title.apply(fam)
store = d.location.str.contains(r'^Store\d{4}', na=False)
s = d[store]
ft = pd.crosstab(s.location_type, s.fam)
print(ft)
ft.to_csv(os.path.join(RAW, 'L3_live2026_family_by_type.csv'))
# req seq windows (2026 numbering): Workday req = YYYY + 5-digit sequence
s26 = s[s.yr == 2026].copy()
s26['win'] = pd.cut(s26.n, [0, 8748, 24157, 34548, 99999], labels=['<=Jun15 (<=8748)', 'Jun15-Jul11 spike (8749-24157)', 'Jul11-Sep2 (24158-34548)', '>Sep2'])
print(pd.crosstab(s26.fam, s26.win))
print(s26.groupby('win', observed=True).startDate.agg(['min', 'max', 'size']))
print('startDate month x family\n', pd.crosstab(s.startDate.dt.to_period('M'), s.fam))
# pay
p = s[s.lo.notna()].copy()
g = p.groupby(['fam', 'title', 'state']).agg(n=('lo', 'size'), lo_med=('lo', 'median'), hi_med=('hi', 'median'), lo_min=('lo', 'min'), lo_max=('lo', 'max')).reset_index()
g.to_csv(os.path.join(RAW, 'L3_live2026_pay_by_title_state.csv'), index=False)
print(p.groupby(['fam', 'state']).agg(n=('lo', 'size'), lo_med=('lo', 'median'), hi_med=('hi', 'median')).unstack('state').round(2).to_string())
print(p.groupby(['title']).agg(n=('lo', 'size'), lo_med=('lo', 'median'), hi_med=('hi', 'median')).query('n>=3').sort_values('lo_med').to_string())
