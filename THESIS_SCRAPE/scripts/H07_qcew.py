"""H07: BLS QCEW county employment in sporting-goods stores (NAICS 451110 through 2021, 459110 from 2022), private (own_code 5),
for all US counties, via the per-industry open files: https://data.bls.gov/cew/data/api/{yr}/{q}/industry/{naics}.csv
Rerun: python H07_qcew.py -> raw/H07_qcew_sporting_allcounties.csv (+ prints HoS-county event table)
"""
import requests, io, pandas as pd
H = {'User-Agent': 'Mozilla/5.0 research'}
frames = []
for yr in range(2019, 2027):
    for q in range(1, 5):
        for naics in ('451110', '459110'):
            r = requests.get(f'https://data.bls.gov/cew/data/api/{yr}/{q}/industry/{naics}.csv', headers=H, timeout=120)
            if r.status_code != 200 or 'area_fips' not in r.text[:300]:
                continue
            d = pd.read_csv(io.StringIO(r.text), dtype={'area_fips': str})
            d = d[d.own_code == 5][['area_fips', 'year', 'qtr', 'industry_code', 'qtrly_estabs', 'month3_emplvl', 'total_qtrly_wages', 'disclosure_code']]
            frames.append(d)
        print(yr, q, flush=True)
df = pd.concat(frames)
df.to_csv(r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\H07_qcew_sporting_allcounties.csv', index=False)
AREAS = {'36069': 'Ontario NY (Victor HoS Apr-21)', '36007': 'Broome NY (Johnson City HoS Aug-23)', '36001': 'Albany NY (Latham HoS Jul-23)',
         '36029': 'Erie NY (Amherst HoS Mar-26)', '36055': 'Monroe NY', '48029': 'Bexar TX (Live Oak HoS Oct-25)', '47093': 'Knox TN (HoS May-21)',
         '19163': 'Scott IA (Davenport HoS Jul-23 remodel)', '20091': 'Johnson KS (Leawood HoS Sep-25)', '51003': 'Albemarle VA (Charlottesville HoS Oct-25)'}
s = df[df.area_fips.isin(AREAS)].copy()
s['area'] = s.area_fips.map(AREAS)
p = s.pivot_table(index=['year', 'qtr'], columns='area', values='month3_emplvl', aggfunc='sum')
pd.set_option('display.width', 300)
print(p.to_string())
