"""B5: scan all 57 non-NYC NY counties for structural breaks in sporting-goods/hobby/music (NAICS 4511->4591) taxable sales,
and refresh the HoS county reads. Re-pulls ny73-2j3u (latest vintage) so preliminary quarters are current.
Method: county share of the 57-county control (excl. NYC, MCTD, state, and the county itself); 4-quarter rolling share;
break = rolling-4Q share vs the prior non-overlapping 4Q share; excess $/yr = delta share x control 4Q total.
Drops known anomalies: Ontario 2025Q3 ($240.9M) and Onondaga 2024Q1.
NY sales-tax quarter q1=Mar-May, q2=Jun-Aug, q3=Sep-Nov, q4=Dec-Feb (yr = sales-tax year start).
Rerun: python scripts/B5_ny_scan.py -> raw/B5_NY_sporting_latest.csv, raw/B5_NY_breaks.csv
"""
import requests, pandas as pd, numpy as np
R = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\\'
rows = requests.get('https://data.ny.gov/resource/ny73-2j3u.json', params={
    '$where': "naics_industry_group in('4511','4591')", '$limit': 50000}, timeout=300).json()
df = pd.DataFrame(rows)
df['v'] = pd.to_numeric(df['taxable_sales_and_purchases'], errors='coerce') / 1e6
df['yr'] = df['sales_tax_year'].str[:4].astype(int)
df['q'] = df['sales_tax_quarter'].astype(int)
df.to_csv(R + 'B5_NY_sporting_latest.csv', index=False)
p = df.pivot_table(index=['yr', 'q'], columns='jurisdiction', values='v', aggfunc='sum').sort_index()
st = df.pivot_table(index=['yr', 'q'], columns='jurisdiction', values='status', aggfunc='first').sort_index()
print('latest quarter:', p.index[-1], 'status', st.iloc[-1].get('ERIE'))
p.loc[(2025, 3), 'ONTARIO'] = np.nan
if (2024, 1) in p.index:
    p.loc[(2024, 1), 'ONODAGA' if 'ONODAGA' in p.columns else 'ONONDAGA'] = np.nan
counties = [c for c in p.columns if c not in ('NY STATE', 'MCTD', 'NY CITY')]
tot = p[counties].sum(axis=1, min_count=50)
out = []
for c in counties:
    ctrl = tot - p[c].fillna(0)
    r4c = p[c].rolling(4).sum(); r4t = ctrl.rolling(4).sum()
    sh = r4c / r4t
    d = sh - sh.shift(4)
    exc = d * r4t
    for i, ix in enumerate(p.index):
        if ix[0] >= 2016 and not np.isnan(exc.iloc[i]):
            out.append(dict(county=c, yr=ix[0], q=ix[1], r4_sales=r4c.iloc[i], share=sh.iloc[i] * 100, d_share_pp=d.iloc[i] * 100,
                            excess_yr=exc.iloc[i], pct_vs_prior=(r4c.iloc[i] / r4c.shift(4).iloc[i] - 1) * 100))
B = pd.DataFrame(out)
B.to_csv(R + 'B5_NY_breaks.csv', index=False)
pd.set_option('display.width', 250)
# largest positive breaks per county (post-2019), excluding pandemic window ending 2021Q1
Bx = B[(B.yr >= 2019)]
top = Bx.sort_values('excess_yr', ascending=False).groupby('county').head(1).sort_values('excess_yr', ascending=False)
print('\nLargest 4Q-vs-prior-4Q excess per county (top 20):')
print(top.head(20).round(2).to_string(index=False))
print('\nMost negative (bottom 10):')
print(Bx.sort_values('excess_yr').groupby('county').head(1).head(10).round(2).to_string(index=False))
for c in ['ONTARIO', 'ALBANY', 'BROOME', 'ERIE', 'MONROE', 'ULSTER', 'SARATOGA', 'DUTCHESS', 'WARREN', 'SCHENECTADY', 'RENSSELAER', 'ONONDAGA', 'NIAGARA']:
    s = p[c]
    print(f'\n{c} quarterly $M (2022q1..):', ' '.join(f'{ix[0]}q{ix[1]}:{v:.1f}' for ix, v in s.loc[(2022, 1):].items()))
