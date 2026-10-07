"""R2: pull all NAICS groups for given counties (data.ny.gov ny73-2j3u) for 2021-2026 and show the biggest y/y changes around a break.
Usage: python R2_county_allnaics.py MONROE 2023 1   -> raw/R2_allnaics_<COUNTY>.csv ; prints groups with largest change y/y in that quarter
"""
import requests, pandas as pd, sys
R = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\\'
c, y, q = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
rows = requests.get('https://data.ny.gov/resource/ny73-2j3u.json', params={
    '$where': f"jurisdiction='{c}' and sales_tax_year >= '2020'", '$limit': 50000}, timeout=300).json()
df = pd.DataFrame(rows)
df['v'] = pd.to_numeric(df['taxable_sales_and_purchases'], errors='coerce') / 1e6
df['yr'] = df['sales_tax_year'].str[:4].astype(int)
df['q'] = df['sales_tax_quarter'].astype(int)
df.to_csv(R + f'R2_allnaics_{c.replace(" ", "_")}.csv', index=False)
desc = df.drop_duplicates('naics_industry_group').set_index('naics_industry_group')['description']
p = df.pivot_table(index='naics_industry_group', columns=['yr', 'q'], values='v', aggfunc='sum')
cur, prev = (y, q), (y - 1, q)
ch = (p[cur] - p[prev]).dropna().sort_values()
out = pd.DataFrame({'desc': desc.reindex(ch.index), 'prev': p[prev].reindex(ch.index).round(2), 'cur': p[cur].reindex(ch.index).round(2), 'chg': ch.round(2)})
pd.set_option('display.width', 250); pd.set_option('display.max_colwidth', 50)
print(out.head(15).to_string()); print(out.tail(8).to_string())
for g in sys.argv[4:]:
    print(g, desc.get(g)); print(p.loc[g].round(2).to_string() if g in p.index else 'n/a')
