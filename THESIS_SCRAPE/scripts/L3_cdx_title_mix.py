"""L3: title mix of archived DICK'S job URLs by requisition creation window (pre vs post Built to Win).
Input: raw/L3_cdx_jobs*.csv (L3_cdx_jobs.py). Each archived URL carries title + location + Workday req id (YYYY + 5-digit seq).
Dedupe by req id; classify title into role families; tabulate by req-creation window (req seq is monotone in time).
Rerun: python L3_cdx_title_mix.py -> raw/L3_cdx_reqs.csv, raw/L3_cdx_title_mix.csv
"""
import pandas as pd, re, os, glob, urllib.parse
pd.set_option('display.width', 250); pd.set_option('display.max_rows', 300)
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'raw')
v = pd.concat([pd.read_csv(f, dtype=str) for f in glob.glob(os.path.join(RAW, 'L3_cdx_jobs*.csv'))]).drop_duplicates(['timestamp', 'original'])


def parse(u):
    u = urllib.parse.unquote_plus(u)
    m = re.search(r'/job/(\d+-)?([a-z0-9\-]+)/([A-Za-z\-\.]+)/(20\d{7})', u)          # /job/<code>-<title>/<city-ST>/<req>/
    if m:
        return m.group(2).replace('-', ' '), m.group(3), m.group(4)
    m = re.search(r'/job/\?(.+)-j-(20\d{7})', u)                                        # /job/?Title-City-ST-j-<req>
    if m:
        parts = m.group(1).split('-')
        return ' '.join(parts[:-2]), '-'.join(parts[-2:]), m.group(2)
    m = re.search(r'/(?:DSG|dsg)/(?:job|details)/(?:([^/]+)/)?([^/?]+?)_(20\d{7})', u)  # workday /DSG/job/<loc>/<Title>_<req>
    if m:
        return m.group(2).replace('-', ' '), m.group(1) or '', m.group(3)
    return None, None, None


rows = []
for r in v.itertuples():
    t, loc, req = parse(r.original)
    if req:
        rows.append([r.timestamp, t, loc, req, r.target])
d = pd.DataFrame(rows, columns=['ts', 'title', 'loc', 'req', 'target'])
d['yr'] = d.req.str[:4].astype(int)
d['seq'] = d.req.str[4:].astype(int)
d = d.sort_values('ts').drop_duplicates('req', keep='first')
d['store'] = d['loc'].str.contains(r'Store\d{4}', na=False) | ~d['loc'].str.contains(r'DC|Customer|Remote|Support', na=True)


def fam(t):
    t = (t or '').lower()
    if 'seasonal' in t: return 'Seasonal'
    if 'team captain' in t: return 'Team Captain (new)'
    if t.startswith('specialist'): return 'Specialist (new)'
    if t.startswith('teammate'): return 'Teammate (new)'
    if t.startswith('advisor'): return 'Advisor (new)'
    if 'assistant store manager' in t: return 'ASM'
    if 'store manager' in t or 'store director' in t: return 'Store Mgr'
    if re.search(r'\blead\b|leader|key holder|keyholder', t): return 'Hourly Lead (old)'
    if re.search(r'engineer|analyst|intern|accountant|designer|director|planner|merchandiser|product manager|co op', t): return 'Corporate'
    if re.search(r'warehouse|shift|dc |distribution|truck|forklift|non con', t): return 'DC/Truck'
    if 'specialist' in t or 'fitter' in t or 'technician' in t or ' tech' in t: return 'Hourly specialist/tech (old)'
    if re.search(r'associate|cashier|assoicate|^retail|ambassador|concierge|teammate', t): return 'Hourly associate (old)'
    return 'Other'


d['fam'] = d.title.apply(fam)
d.to_csv(os.path.join(RAW, 'L3_cdx_reqs.csv'), index=False)
# windows by req id: 2025 full year by quarter-ish seq bands; 2026 pre/post cutover (seq 8,748 = 2026-06-15 per H06 Wayback)
def win(r):
    if r.yr < 2025: return f'{r.yr}'
    if r.yr == 2025: return '2025 seq<=10000 (Jan-~Jun)' if r.seq <= 10000 else '2025 seq>10000 (~Jun-Dec)'
    if r.seq <= 8748: return '2026 pre-cutover (<=Jun15)'
    return '2026 post-cutover (>Jun15)'


d['win'] = d.apply(win, axis=1)
s = d[d.fam.isin(['Seasonal', 'Team Captain (new)', 'Specialist (new)', 'Teammate (new)', 'Advisor (new)', 'ASM', 'Store Mgr', 'Hourly Lead (old)', 'Hourly specialist/tech (old)', 'Hourly associate (old)'])]
ct = pd.crosstab(s.win, s.fam, margins=True)
print(ct.to_string())
sh = pd.crosstab(s.win, s.fam, normalize='index').mul(100).round(1)
print(sh.to_string())
pd.concat([ct, sh.add_suffix(' %')], axis=1).to_csv(os.path.join(RAW, 'L3_cdx_title_mix.csv'))
print(d[(d.fam == 'ASM')].groupby('win').title.apply(lambda x: x.str.lower().str.replace(r'[^a-z ]', ' ', regex=True).str.split().str[3:].str.join(' ').value_counts().head(8).to_dict()).to_string())
