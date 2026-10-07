"""D06: pull Census retail sales (sporting goods) + CPI sporting goods from FRED (no key needed).
Rerun: python THESIS_SCRAPE/scripts/D06_census_fred.py
Output: THESIS_SCRAPE/raw/D06_census_fred.csv (levels + y/y) and printed table.
Series:
  RSSGHBMS       Advance retail sales: sporting goods, hobby, musical instrument & book stores (NAICS 451), SA, $M
  MRTSSM451USS   MRTS NAICS 451, SA, $M (lags advance by 1 month)
  MRTSSM451USN   MRTS NAICS 451, NSA
  MRTSSM45111USN MRTS NAICS 45111 sporting goods stores only, NSA, $M
  MRTSSM45111USS MRTS 45111 SA (if exists)
  RSXFS          Advance retail sales ex food services, SA
  CUUR0000SERC   CPI sporting goods (NSA)  -> real growth deflator
  CUUR0000SEAE   CPI footwear
  CUSR0000SAA    CPI apparel
"""
import io, requests, pandas as pd, os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDS = ['RSSGHBMS','MRTSSM451USS','MRTSSM451USN','MRTSSM45111USN','MRTSSM45111USS','RSXFS',
       'CUUR0000SERC','CUUR0000SEAE','CUSR0000SAA','CUUR0000SERC01','CUUR0000SERC02']
frames = []
for s in IDS:
    r = requests.get('https://fred.stlouisfed.org/graph/fredgraph.csv?id=' + s, timeout=60)
    if r.status_code != 200 or not r.text.startswith('observation_date'):
        print('missing', s); continue
    df = pd.read_csv(io.StringIO(r.text), index_col=0, parse_dates=True)
    df[s] = pd.to_numeric(df[s], errors='coerce')
    frames.append(df)
d = pd.concat(frames, axis=1)
d = d[d.index >= '2018-01-01']
yy = d.pct_change(12, fill_method=None) * 100
yy.columns = [c + '_yy' for c in yy.columns]
out = pd.concat([d, yy], axis=1)
out.to_csv(os.path.join(BASE, 'raw', 'D06_census_fred.csv'))
pd.set_option('display.width', 250); pd.set_option('display.max_columns', 30)
print(yy[yy.index >= '2024-07-01'].round(2).to_string())
