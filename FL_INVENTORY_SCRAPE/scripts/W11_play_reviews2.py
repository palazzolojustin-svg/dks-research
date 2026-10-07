"""W11: single-call Google Play review pull (count=N) per app; writes raw/W11/play2_<pkg>.csv"""
import sys, os, time
import pandas as pd
from google_play_scraper import reviews, Sort, app
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'raw', 'W11')
for p in ["com.footlocker.approved","com.champssports.champssports","com.footlocker.kids","com.WinnersCircle","com.jd.jdsportsusa","com.hibbett.android","dsgui.android"]:
    out=os.path.join(RAW,f'play2_{p}.csv')
    if os.path.exists(out): continue
    r,_=reviews(p,lang='en',country='us',sort=Sort.NEWEST,count=8000)
    d=pd.DataFrame(r)[['reviewId','at','score','thumbsUpCount','appVersion','content']]
    d.to_csv(out,index=False); print(p,len(d),d['at'].min(),flush=True); time.sleep(3)
