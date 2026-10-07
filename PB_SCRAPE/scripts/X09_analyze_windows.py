"""X09: analyse matched-window Google Trends pulls (Apify apify/google-trends-scraper output saved as
raw/X09_apify_windows*.json, OR raw/X09_gt_win_*.csv from X09_run_windows.py).
For each batch, computes each term's SUM of daily values in the window and its share of the batch total,
then compares the same batch across windows (2026 vs 2025).  Ratios within a window are scale-free, so
share changes are comparable even though each window is normalised separately.
Rerun: python X09_analyze_windows.py  -> raw/X09_gt_windows_summary.csv
"""
import json, glob, os, re, urllib.parse as up
import pandas as pd
RAW = os.path.join(os.path.dirname(__file__), '..', 'raw')
rows = []
for f in glob.glob(os.path.join(RAW, 'X09_apify_windows*.json')):
    for it in json.load(open(f, encoding='utf-8')):
        url = it['inputUrlOrTerm']
        q = up.parse_qs(up.urlparse(url).query)
        terms = q['q'][0].split(',')
        win = q['date'][0]
        tl = it.get('interestOverTime_timelineData') or []
        sums = [0.0] * len(terms)
        for p in tl:
            for i, v in enumerate(p['value']):
                sums[i] += v
        for t, s in zip(terms, sums):
            rows.append(dict(window=win, batch=','.join(terms), term=t, sum=s, ndays=len(tl)))
for f in glob.glob(os.path.join(RAW, 'X09_gt_win_*.csv')):
    df = pd.read_csv(f, index_col=0)
    win = os.path.basename(f)[11:14]
    for t in df.columns:
        rows.append(dict(window=win, batch=','.join(df.columns), term=t, sum=df[t].sum(), ndays=len(df)))
d = pd.DataFrame(rows).drop_duplicates(['window', 'batch', 'term'])
d['share%'] = d['sum'] / d.groupby(['window', 'batch'])['sum'].transform('sum') * 100
d.to_csv(os.path.join(RAW, 'X09_gt_windows_summary.csv'), index=False)
pv = d.pivot_table(index=['batch', 'term'], columns='window', values='share%')
pd.set_option('display.width', 250)
print(pv.round(2).to_string())
