"""B11: Minnesota DOR annual sales & use tax by city x 3-digit industry (Minnetonka) and statewide 3-digit, 2018-2024.
Complements B5's raw/B5_mn files (missing Minnetonka 2023 and state 2024). Rerun: python scripts/B11_mn_fetch.py"""
import requests, re, time, os
H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124'}
OUT = 'raw/B11_cache/mn'; os.makedirs(OUT, exist_ok=True)
def get(u):
    for a in range(5):
        try:
            r = requests.get(u, headers=H, timeout=60)
            if r.status_code == 200: return r
            print('status', r.status_code, u)
        except Exception as e: print('err', e)
        time.sleep(5)
for y, page in [('2023', 'https://revenue.state.mn.us/2023-sales-and-use-tax-revenue-city-0'), ('2024', 'https://www.revenue.state.mn.us/2024-sales-and-use-tax-revenue-city'), ('2022', 'https://www.revenue.state.mn.us/2022-sales-and-use-tax-revenue-city')]:
    r = get(page)
    if r is None: continue
    links = [l for l in set(re.findall(r'href="([^"#]+)"', r.text)) if 'minnetonka' in l.lower()]
    print(y, links)
    for l in links:
        u = l if l.startswith('http') else 'https://www.revenue.state.mn.us' + l
        f = get(u)
        if f is not None: open(f'{OUT}/minnetonka_{y}.xlsx', 'wb').write(f.content); print('saved', y, len(f.content))
for y, u in [('2024', '/sites/default/files/2026-06/mn-state-3-digit-industry-code-2024.xlsx'), ('2023', '/sites/default/files/2025-06/mn-state-3-digit-industry-code-2023.xlsx'),
             ('2024_4d', '/sites/default/files/2026-06/mn-state-4-digit-industry-code-2024.xlsx'), ('2023_4d', '/sites/default/files/2025-06/mn-state-4-digit-industry-code-2023.xlsx')]:
    f = get('https://www.revenue.state.mn.us' + u)
    if f is not None: open(f'{OUT}/state_{y}.xlsx', 'wb').write(f.content); print('saved state', y, len(f.content))
