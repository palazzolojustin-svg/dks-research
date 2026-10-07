"""B11: MN statewide 3-digit (and 4-digit) industry files for 2018-2022 via the statistics pages. Rerun: python scripts/B11_mn_fetch2.py"""
import requests, re, time, os
H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124'}
OUT = 'raw/B11_cache/mn'
def get(u):
    for a in range(6):
        try:
            r = requests.get(u, headers=H, timeout=60)
            if r.status_code == 200: return r
        except Exception: pass
        time.sleep(4)
for y in ['2018', '2019', '2020', '2021', '2022']:
    r = get(f'https://www.revenue.state.mn.us/sales-and-use-tax-statistics-{y}')
    if r is None: print(y, 'page fail'); continue
    for l in set(re.findall(r'href="([^"#]+)"', r.text)):
        if re.search(r'(?i)(3|4)-digit', l) and l.lower().endswith(('.xlsx', '.xls')):
            tag = '4d' if '4-digit' in l.lower() else '3d'
            f = get(l if l.startswith('http') else 'https://www.revenue.state.mn.us' + l)
            print(y, tag, l, f is not None)
            if f is not None: open(f'{OUT}/state_{y}_{tag}.xlsx', 'wb').write(f.content)
