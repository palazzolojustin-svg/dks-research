"""B11: check latest quarter in TX Comptroller quarterly city x sector data (7z4d-yf2c) and pull Retail Trade for event + control cities.
Rerun: python scripts/B11_tx_check.py"""
import requests, datetime, pandas as pd
B = 'https://data.texas.gov/resource/7z4d-yf2c.json'
r = requests.get(B, params={'$select': 'year,qtr,count(*)', '$group': 'year,qtr', '$order': 'year desc,qtr desc', '$limit': 4}, timeout=120); print(r.text)
m = requests.get('https://data.texas.gov/api/views/7z4d-yf2c.json', timeout=60).json()
print('rowsUpdatedAt', datetime.datetime.fromtimestamp(m.get('rowsUpdatedAt')))
cities = ['Live Oak', 'Selma', 'Universal City', 'Converse', 'Schertz', 'Windcrest', 'San Antonio', 'Arlington', 'Grand Prairie', 'Mansfield', 'Fort Worth', 'Frisco', 'Dallas']
rows = []
for c in cities:
    j = requests.get(B, params={'$where': f"upper(name)='{c.upper()}' and type='City' and industry='Retail Trade' and year>=2023", '$limit': 1000}, timeout=120).json()
    rows += j
d = pd.DataFrame(rows); d['taxable'] = pd.to_numeric(d.taxable) / 1e6
pv = d.pivot_table(index=['year', 'qtr'], columns='name', values='taxable').round(1)
pd.set_option('display.width', 250); print(pv.to_string())
pv.to_csv('raw/B11_TX_retail_taxable.csv')
