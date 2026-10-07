"""B4: NY taxable sales (data.ny.gov ny73-2j3u), NAICS 4511/4591 Sporting Goods, Hobby & Musical Instrument stores,
for counties with a DICK'S Field House / next-gen relocation (Tompkins = Ithaca #156->#1535 ~Dec-2023;
Jefferson = Watertown #158->#1545 ~Apr-2024; Ulster = Kingston #154->#1622 Mar-2026; Monroe = Rochester #427->#1630 ~2025),
plus a closure control (Cayuga = Auburn #705 dropped ~Jul-2025) and NY State.
NY sales-tax quarters: Q1=Mar-May, Q2=Jun-Aug, Q3=Sep-Nov, Q4=Dec-Feb (sales_tax_year starts in March).
Output: raw/B4_ny_fh_counties.csv (quarterly levels, y/y growth, county minus state y/y).
Rerun: python B4_ny_fh_counties.py
"""
import requests, pandas as pd
R = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\\'
rows = requests.get('https://data.ny.gov/resource/ny73-2j3u.json', params={
    '$where': "naics_industry_group in('4511','4591')", '$limit': 50000}, timeout=300).json()
df = pd.DataFrame(rows)
df['v'] = pd.to_numeric(df['taxable_sales_and_purchases'], errors='coerce')
df['yr'] = df['sales_tax_year'].str[:4].astype(int)
df['q'] = df['sales_tax_quarter'].astype(int)
df.to_csv(R + 'B4_ny_4511_all_counties.csv', index=False)
p = df.pivot_table(index=['yr', 'q'], columns='jurisdiction', values='v', aggfunc='sum').sort_index()
cols = ['NY STATE', 'TOMPKINS', 'JEFFERSON', 'ULSTER', 'MONROE', 'CAYUGA', 'ONTARIO', 'BROOME', 'ST LAWRENCE', 'OSWEGO', 'CORTLAND', 'CHEMUNG']
cols = [c for c in cols if c in p.columns]
lv = p[cols] / 1e6
yoy = p[cols].pct_change(4) * 100
rel = yoy.sub(yoy['NY STATE'], axis=0)
out = pd.concat({'level_$M': lv.round(2), 'yoy_%': yoy.round(1), 'rel_to_state_pp': rel.round(1)}, axis=1)
out.to_csv(R + 'B4_ny_fh_counties.csv')
pd.set_option('display.width', 300); pd.set_option('display.max_columns', 50)
print(lv.round(2).tail(24).to_string())
print(rel[['TOMPKINS', 'JEFFERSON', 'ULSTER', 'MONROE', 'CAYUGA']].round(1).tail(24).to_string())
print(sorted(p.columns.tolist()))
