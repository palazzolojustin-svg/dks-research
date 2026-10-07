"""B4: Texas 'All Permitted Sales Tax Locations' (3kx8-uryv) for DICK'S taxpayer 11612415379 incl. inactive outlets.
Rerun: python B4_tx_outlets.py -> raw/B4_tx_outlets_all.csv"""
import requests, pandas as pd
B = 'https://data.texas.gov/resource/'
j = requests.get(B + '3kx8-uryv.json', params={'$where': "taxpayer_number='11612415379'", '$limit': 500}, timeout=120).json()
df = pd.DataFrame(j)
print(df.shape, df.columns.tolist())
df.to_csv(r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\B4_tx_outlets_all.csv', index=False)
