"""R2: fresh pull of NY taxable sales (data.ny.gov ny73-2j3u) NAICS 4511/4591 (sporting goods/hobby/music) + metadata,
plus a few comparison industry groups (4481 clothing, 4482 shoe, 4529 general merch, 4521 dept stores) for county-level controls.
Rerun: python R2_ny_pull.py -> raw/R2_ny_4511.csv, raw/R2_ny_ctrl.csv, raw/R2_ny_meta.txt
"""
import requests, pandas as pd, datetime, json
R = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\\'
m = requests.get('https://data.ny.gov/api/views/ny73-2j3u.json', timeout=60).json()
meta = {k: str(datetime.datetime.utcfromtimestamp(m.get(k, 0))) for k in ['rowsUpdatedAt', 'viewLastModified', 'publicationDate']}
grp = requests.get('https://data.ny.gov/resource/ny73-2j3u.json', params={
    '$select': 'sales_tax_year,sales_tax_quarter,count(*)', '$group': 'sales_tax_year,sales_tax_quarter',
    '$order': 'sales_tax_year desc,sales_tax_quarter desc', '$limit': 8}, timeout=120).json()
sample = requests.get('https://data.ny.gov/resource/ny73-2j3u.json', params={'$limit': 2}, timeout=60).json()
open(R + 'R2_ny_meta.txt', 'w').write(json.dumps({'meta': meta, 'latest_quarters': grp, 'sample': sample}, indent=1))
print(json.dumps({'meta': meta, 'latest_quarters': grp, 'sample': sample}, indent=1))
rows = requests.get('https://data.ny.gov/resource/ny73-2j3u.json', params={
    '$where': "naics_industry_group in('4511','4591')", '$limit': 50000}, timeout=300).json()
df = pd.DataFrame(rows)
df.to_csv(R + 'R2_ny_4511.csv', index=False)
print(len(df), df.columns.tolist())
ctl = requests.get('https://data.ny.gov/resource/ny73-2j3u.json', params={
    '$where': "naics_industry_group in('4481','4482','4521','4522','4529','4551','4552','4552')", '$limit': 200000}, timeout=300).json()
pd.DataFrame(ctl).to_csv(R + 'R2_ny_ctrl.csv', index=False)
print(len(ctl))
