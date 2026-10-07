"""L6: download state WARN spreadsheets (xlsx/xls/csv) and grep all cells for DKS-family names; prints
row count and date range so coverage is explicit.
Usage: python L6_xlsx_grep.py <url> [<url> ...]   (files cached in THESIS_SCRAPE\\raw\\L6_state\\)
"""
import requests, re, os, sys, time, io
import pandas as pd
H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) research palazzolojustin@gmail.com'}
D = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\L6_state'; os.makedirs(D, exist_ok=True)
PAT = re.compile(r"dick.{0,2}s\s*sporting|golf\s*galaxy|going,?\s*going|foot\s*locker|footlocker|public\s*lands|champs\s*sports|\bdsg\b", re.I)

def get(u):
    for i in range(6):
        try:
            r = requests.get(u, headers=H, timeout=120)
            if r.status_code == 200:
                return r.content
            print('status', r.status_code); return None
        except Exception as e:
            print('retry', type(e).__name__); time.sleep(3 + 3 * i)

for u in sys.argv[1:]:
    p = os.path.join(D, re.sub(r'[^A-Za-z0-9.]+', '_', u)[-100:])
    if not os.path.exists(p):
        b = get(u)
        if not b:
            print('FAILED', u); continue
        open(p, 'wb').write(b)
    try:
        if p.lower().endswith('.csv'):
            sheets = {'csv': pd.read_csv(p, dtype=str, encoding_errors='replace')}
        else:
            sheets = pd.read_excel(p, sheet_name=None, dtype=str)
    except Exception as e:
        print('READ FAIL', u, e); continue
    for sn, df in sheets.items():
        df = df.fillna('')
        joined = df.astype(str).agg(' | '.join, axis=1)
        dates = pd.to_datetime(pd.Series(re.findall(r'20\d\d-\d\d-\d\d', ' '.join(joined))), errors='coerce').dropna()
        print(u.split('/')[-1], sn, 'rows', len(df), 'dates', dates.min() if len(dates) else None, dates.max() if len(dates) else None)
        for line in joined[joined.str.contains(PAT)]:
            print('  HIT', line[:400])
