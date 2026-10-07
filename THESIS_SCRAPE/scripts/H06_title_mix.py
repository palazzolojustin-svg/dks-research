"""H06: store-role title mix before vs after the 'Built to Win' store labor model (summer 2026).
Inputs: raw/H06_sitemap_<ts>.txt (Wayback copies of dickssportinggoods.jobs/jobs-sitemap.xml) and raw/H06_workday_postings_2026-10-07.csv.
Rerun: python H06_title_mix.py -> raw/H06_title_mix.csv
"""
import re, glob, os, collections, pandas as pd
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'raw')


def cls(t):
    t = t.lower().replace('-', ' ')
    if 'house of sport' in t and ('director' in t or 'store manager' in t and 'assistant' not in t): return 'HoS SM/ESD'
    if 'executive store director' in t or ('store manager' in t and 'assistant' not in t and 'loss' not in t): return 'Store Mgr (incl bench)'
    if 'assistant store manager' in t: return 'ASM'
    if 'team captain' in t: return 'Team Captain (new)'
    if 'specialist' in t and 'loss prevention' not in t and 'customer service' not in t and 'visual' not in t and 'marketing' not in t: return 'Specialist (new)'
    if re.search(r'teammate (sales|operations)$', t.strip()) or t.strip() in ('teammate sales', 'teammate operations'): return 'Teammate evergreen (new)'
    if 'advisor' in t: return 'Advisor (new)'
    if 'seasonal' in t: return 'Seasonal'
    if re.search(r'\blead\b|leader|key holder|supervisor', t): return 'Hourly Lead (old)'
    if 'associate' in t or 'cashier' in t or 'technician' in t or 'tech' in t: return 'Hourly associate (old)'
    if 'teammate' in t: return 'Teammate other (new)'
    return 'Other'


rows = []
for f in sorted(glob.glob(os.path.join(RAW, 'H06_sitemap_*.txt'))):
    ts = re.search(r'H06_sitemap_(\d{14})', f)
    if not ts:
        continue
    urls = [u for u in open(f, encoding='utf-8').read().split() if '/job/' in u]
    if not urls:
        continue
    c = collections.Counter()
    locs = set()
    for u in urls:
        m = re.search(r'/job/([^/?]+)/([^/]+)/', u)
        if m:
            title, loc = m.group(1), m.group(2)
        else:  # 2024 format: /job/?Title+Words-City-ST-j-reqid
            m = re.search(r'/job/\?(.+)-j-\d+', u)
            if not m:
                continue
            parts = m.group(1).replace('+', ' ').rsplit('-', 2)
            title, loc = parts[0], '-'.join(parts[1:])
        c[cls(title)] += 1
        locs.add(loc)
    for k, v in c.items():
        rows.append([ts.group(1)[:8], k, v, len(urls), len(locs)])
p = pd.read_csv(sorted(glob.glob(os.path.join(RAW, 'H06_workday_postings_*.csv')))[-1])
p = p[p.location.str.contains('Store', na=False)]
c = collections.Counter(p.title.map(cls))
for k, v in c.items():
    rows.append(['20261007wd', k, v, len(p), p.location.nunique()])
df = pd.DataFrame(rows, columns=['date', 'class', 'n', 'total', 'n_locs'])
pv = df.pivot_table(index='class', columns='date', values='n', aggfunc='sum').fillna(0).astype(int)
tot = df.groupby('date').total.first()
print(pv.to_string()); print(tot.to_string())
print((pv / tot * 100).round(1).to_string())
df.to_csv(os.path.join(RAW, 'H06_title_mix.csv'), index=False)
