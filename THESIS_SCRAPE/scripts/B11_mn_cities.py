"""B11: MN city x industry annual files for Minnetonka + Twin Cities control cities, 2021-2024 (URL pattern from MN DOR site).
Then compute 451+453 (2021) vs 459 (2022+) gross and taxable, Minnetonka vs controls and state.
Rerun: python scripts/B11_mn_cities.py -> raw/B11_MN_459.csv"""
import requests, time, os, pandas as pd, warnings, glob
warnings.filterwarnings('ignore')
H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124'}
OUT = 'raw/B11_cache/mn'
PFX = {'2021': ['2023-07', '2022-12', '2023-01', '2023-02', '2023-03', '2023-06'], '2022': ['2024-02'], '2023': ['2025-06'], '2024': ['2026-06']}
cities = ['minnetonka', 'edina', 'bloomington', 'roseville', 'maple-grove', 'woodbury', 'eden-prairie', 'plymouth', 'burnsville', 'st-louis-park', 'blaine', 'coon-rapids', 'eagan', 'lakeville', 'st-cloud', 'rochester']
def get(u):
    for a in range(4):
        try:
            r = requests.get(u, headers=H, timeout=60)
            if r.status_code == 200 and r.content[:2] == b'PK': return r
            if r.status_code == 404: return None
        except Exception: pass
        time.sleep(3)
for c in cities:
    for y, pf in PFX.items():
        fn = f'{OUT}/{c}_{y}.xlsx'
        if os.path.exists(fn): continue
        for p in pf:
            r = get(f'https://www.revenue.state.mn.us/sites/default/files/{p}/{c}-city-industry-{y}.xlsx')
            if r is not None:
                open(fn, 'wb').write(r.content); print('saved', c, y); break
        else:
            print('miss', c, y)
# also reuse B5 minnetonka 2021
import shutil
if not os.path.exists(f'{OUT}/minnetonka_2021.xlsx') and os.path.exists('raw/B5_mn/minnetonka_2021.xlsx'):
    shutil.copy('raw/B5_mn/minnetonka_2021.xlsx', f'{OUT}/minnetonka_2021.xlsx')
rows = []
for f in glob.glob(f'{OUT}/*_20*.xlsx'):
    b = os.path.basename(f)[:-5]
    if b.startswith('state'): continue
    c, y = b.rsplit('_', 1)
    d = pd.read_excel(f, header=None)
    for _, r in d.iterrows():
        s = str(r[2])
        if s[:3] in ('451', '453', '459', '448', '458'):
            rows.append(dict(city=c, year=int(y), code=s[:3], gross=float(r[3]), taxable=float(r[4]), n=r[8]))
p = pd.DataFrame(rows)
p['grp'] = p.code.map({'451': 'L', '453': 'L', '459': 'L', '448': 'C', '458': 'C'})
a = p.groupby(['city', 'year', 'grp'])[['gross', 'taxable']].sum().reset_index()
a.to_csv('raw/B11_MN_459.csv', index=False)
pd.set_option('display.width', 250)
print((a[a.grp == 'L'].pivot_table(index='city', columns='year', values='gross') / 1e6).round(1).to_string())
print((a[a.grp == 'L'].pivot_table(index='city', columns='year', values='taxable') / 1e6).round(1).to_string())
print((a[a.grp == 'C'].pivot_table(index='city', columns='year', values='gross') / 1e6).round(1).to_string())
