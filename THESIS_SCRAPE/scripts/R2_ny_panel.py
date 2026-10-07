"""R2: build quarterly county panel ($M) for NAICS 4511/4591 and print candidate counties.
Rerun: python R2_ny_panel.py -> raw/R2_ny_panel.csv
NY quarter q1=Mar-May, q2=Jun-Aug, q3=Sep-Nov, q4=Dec-Feb; yr = start year of sales-tax year.
"""
import pandas as pd, sys
R = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\\'
df = pd.read_csv(R + 'R2_ny_4511.csv')
df['v'] = pd.to_numeric(df['taxable_sales_and_purchases'], errors='coerce')
df['yr'] = df['sales_tax_year'].str[:4].astype(int)
df['q'] = df['sales_tax_quarter'].astype(int)
print(df.groupby(['naics_industry_group'])['yr'].agg(['min', 'max', 'count']))
p = df.pivot_table(index=['yr', 'q'], columns='jurisdiction', values='v', aggfunc='sum').sort_index() / 1e6
p.to_csv(R + 'R2_ny_panel.csv')
cols = sys.argv[1:] or ['NY STATE', 'CLINTON', 'WARREN', 'OTSEGO', 'GENESEE', 'CHEMUNG', 'ONEIDA', 'ORANGE', 'MONROE', 'NIAGARA', 'DUTCHESS', 'STEUBEN', 'CHAUTAUQUA']
pd.set_option('display.width', 300); pd.set_option('display.max_columns', 40)
print(p[[c for c in cols if c in p.columns]].round(2).loc[2017:].to_string())
st = df[['jurisdiction', 'yr', 'q', 'status']].drop_duplicates()
print(st[st.jurisdiction == 'NY STATE'].sort_values(['yr', 'q']).tail(16).to_string())
