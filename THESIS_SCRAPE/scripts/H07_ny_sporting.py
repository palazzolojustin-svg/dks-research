"""H07: New York State taxable sales by county for NAICS 4511/4591 (Sporting Goods, Hobby & Musical Instrument
stores/retailers), from data.ny.gov dataset ny73-2j3u (Taxable Sales And Purchases Quarterly Data).
NY sales-tax quarters: Q1 = Mar-May, Q2 = Jun-Aug, Q3 = Sep-Nov, Q4 = Dec-Feb. Status P = preliminary, F = final.
Rerun: python H07_ny_sporting.py -> raw/H07_NY_sporting_by_county.csv and prints a pivot.
"""
import requests, pandas as pd
rows = requests.get('https://data.ny.gov/resource/ny73-2j3u.json', params={
    '$where': "naics_industry_group in('4511','4591','4510','4590')", '$limit': 50000}, timeout=300).json()
df = pd.DataFrame(rows)
df['taxable_sales_and_purchases'] = pd.to_numeric(df['taxable_sales_and_purchases'], errors='coerce')
df['yr'] = df['sales_tax_year'].str[:4].astype(int)
df['q'] = df['sales_tax_quarter'].astype(int)
df.to_csv(r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\H07_NY_sporting_by_county.csv', index=False)
p = df.pivot_table(index=['yr', 'q'], columns='jurisdiction', values='taxable_sales_and_purchases', aggfunc='sum')
pd.set_option('display.width', 250)
cols = [c for c in ['NY STATE', 'ONTARIO', 'MONROE', 'BROOME', 'ERIE', 'ALBANY', 'SARATOGA', 'SCHENECTADY', 'NASSAU', 'SUFFOLK', 'WESTCHESTER', 'ONONDAGA'] if c in p.columns]
print((p[cols] / 1e6).round(1).to_string())
