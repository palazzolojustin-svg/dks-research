"""D06: Google Trends (pytrends) weekly US search interest, last 5y, for DKS and peers.
Rerun: python THESIS_SCRAPE/scripts/D06_gtrends.py   (Google may 429; script sleeps & retries)
Output: THESIS_SCRAPE/raw/D06_gtrends_<set>.csv and printed y/y by DKS fiscal quarter (weeks mapped by week-start date).
Note: each request is normalised 0-100 within its own term set; y/y ratios within a term are valid.
"""
import time, os, sys, pandas as pd
from pytrends.request import TrendReq
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SETS = {
    'dks_peers': ['dicks sporting goods', 'academy sports', 'scheels', 'foot locker', 'big 5 sporting goods'],
    'dks_formats': ['dicks sporting goods', 'house of sport', 'dicks house of sport', 'golf galaxy', 'going going gone'],
}
py = TrendReq(hl='en-US', tz=300, timeout=(10, 30))
for name, kw in SETS.items():
    for attempt in range(5):
        try:
            py.build_payload(kw, timeframe='today 5-y', geo='US')
            df = py.interest_over_time()
            break
        except Exception as e:
            print('retry', name, e); time.sleep(30 * (attempt + 1))
    else:
        print('FAILED', name); continue
    df = df.drop(columns=['isPartial'], errors='ignore')
    df.to_csv(os.path.join(BASE, 'raw', f'D06_gtrends_{name}.csv'))
    time.sleep(20)
print('done')
