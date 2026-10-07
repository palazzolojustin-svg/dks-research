"""X14: analyse DKS vertical-brand factory disclosure lists (Transparency Pledge exports).
Inputs: PB_SCRAPE/raw/X14_fl_*.xlsx (+ X14_fl_2020-09.pdf parsed separately).
Outputs: PB_SCRAPE/raw/X14_factory_list_summary.csv, X14_factory_list_combined.csv, X14_vendor_counts.csv
Rerun: python X14_factory_list_analysis.py  (drop any newer list into raw/ named X14_fl_YYYY-MM.xlsx)
"""
import pandas as pd, glob, os, re, warnings
warnings.filterwarnings('ignore')
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'raw')
frames = []
for f in sorted(glob.glob(os.path.join(RAW, 'X14_fl_*.xlsx'))):
    ver = re.search(r'X14_fl_(\d{4}-\d{2})', f).group(1)
    d = pd.read_excel(f, sheet_name='Details', header=0)
    d['ver'] = ver
    frames.append(d)
df = pd.concat(frames, ignore_index=True)
df['Country'] = df['Country'].astype(str).str.replace('Taiwan, Province of China', 'Taiwan').str.strip()
df['fkey'] = df['Factory Name'].astype(str).str.lower().str.replace(r'[^a-z0-9]', '', regex=True)
df.to_csv(os.path.join(RAW, 'X14_factory_list_combined.csv'), index=False)
rows = []
for ver, g in df.groupby('ver'):
    for tier in ['ALL', 'Tier 1', 'Tier 2']:
        h = g if tier == 'ALL' else g[g['Factory Tier'] == tier]
        rows.append({'ver': ver, 'tier': tier, 'rows': len(h), 'factories': h['fkey'].nunique(),
                     'vendors': h['Vendor Name'].nunique(), 'countries': h['Country'].nunique(),
                     'workers_sum': pd.to_numeric(h['Total Number of Workers'], errors='coerce').sum(),
                     **{f'type_{k}': v for k, v in h.drop_duplicates('fkey')['Factory Type'].value_counts().items()},
                     **{f'cty_{k}': v for k, v in h.drop_duplicates('fkey')['Country'].value_counts().head(12).items()}})
s = pd.DataFrame(rows).fillna(0)
s.to_csv(os.path.join(RAW, 'X14_factory_list_summary.csv'), index=False)
pd.set_option('display.width', 250); pd.set_option('display.max_columns', 60)
print(s.T.to_string())
# Tier-1 churn between versions
t1 = {v: set(g[g['Factory Tier'] == 'Tier 1']['fkey']) for v, g in df.groupby('ver')}
vs = sorted(t1)
for a, b in zip(vs, vs[1:]):
    print(f'T1 {a}->{b}: kept {len(t1[a] & t1[b])}, new {len(t1[b]-t1[a])}, dropped {len(t1[a]-t1[b])}')
vc = df[df['Factory Tier'] == 'Tier 1'].drop_duplicates(['ver', 'fkey']).groupby(['Vendor Name', 'ver']).size().unstack(fill_value=0)
vc['tot'] = vc.sum(axis=1)
vc.sort_values('tot', ascending=False).to_csv(os.path.join(RAW, 'X14_vendor_counts.csv'))
print(vc.sort_values('tot', ascending=False).head(40).to_string())
