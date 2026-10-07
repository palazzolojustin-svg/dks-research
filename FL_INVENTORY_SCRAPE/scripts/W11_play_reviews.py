"""W11: pull Google Play reviews (newest first) back to 2024-01-01 for FL-family and peer apps.
Output raw/W11/play_<pkg>.csv (reviewId, at, score, thumbsUp, appVersion, content)."""
import time, os, sys, datetime as dt
import pandas as pd
from google_play_scraper import reviews, Sort
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'raw', 'W11')
PK = sys.argv[1:] or ["com.footlocker.approved","com.champssports.champssports","com.footlocker.kids","com.WinnersCircle","com.jd.jdsportsusa","dsgui.android"]
STOP = dt.datetime(2024,1,1)
for pkg in PK:
    out = os.path.join(RAW, f'play_{pkg}.csv')
    if os.path.exists(out): print('skip', pkg); continue
    rows, tok = [], None
    while True:
        for a in range(4):
            try:
                res, tok = reviews(pkg, lang='en', country='us', sort=Sort.NEWEST, count=200, continuation_token=tok); break
            except Exception as e:
                print('err', pkg, e, file=sys.stderr); time.sleep(10*(a+1)); res=[]
        if not res: break
        rows += [{k: r.get(k) for k in ('reviewId','at','score','thumbsUpCount','appVersion','content')} for r in res]
        if res[-1]['at'] < STOP or tok is None or getattr(tok,'token',1) is None: break
        time.sleep(1.0)
    df = pd.DataFrame(rows); df.to_csv(out, index=False)
    print(pkg, len(df), df['at'].min() if len(df) else None, flush=True)
