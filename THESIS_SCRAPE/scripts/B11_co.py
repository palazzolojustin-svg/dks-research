"""B11: Colorado DOR retail sales by city x NAICS (data.colorado.gov k3gg-hhc8). Latest month + NAICS 451/459 for DKS-relevant cities.
Rerun: python scripts/B11_co.py -> raw/B11_CO_city_naics.csv"""
import requests, pandas as pd
B = 'https://data.colorado.gov/resource/k3gg-hhc8.json'
print(requests.get(B, params={'$select': 'year,month,count(*)', '$group': 'year,month', '$order': 'year desc, month desc', '$limit': 3}, timeout=120).text[:400])
print(requests.get(B, params={'$limit': 2}, timeout=120).text[:800])
cities = ['Thornton', 'Broomfield', 'Northglenn', 'Westminster', 'Denver', 'Lone Tree', 'Littleton', 'Aurora', 'Colorado Springs', 'Fort Collins', 'Loveland', 'Longmont', 'Lakewood', 'Pueblo', 'Grand Junction', 'Glendale', 'Boulder', 'Castle Rock', 'Parker', 'Greeley']
inlist = ','.join(f"'{c}'" for c in cities)
j = requests.get(B, params={'$where': f"city in({inlist}) and (naics like '451%' or naics like '459%')", '$limit': 50000}, timeout=300).json()
d = pd.DataFrame(j); d.to_csv('raw/B11_CO_city_naics.csv', index=False); print(d.shape, d.columns.tolist()); print(d.naics.value_counts().head())
