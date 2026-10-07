"""W11: monthly Tranco (30-day combined CrUX/Radar/Umbrella/Majestic/Farsight) ranks for FL-family + peer domains.
Downloads top-200K of the daily list nearest the 6th of each month; writes data/W11_tranco_ranks.csv"""
import requests, time, io, os, csv, datetime as dt
DOM=["footlocker.com","champssports.com","kidsfootlocker.com","finishline.com","jdsports.com","hibbett.com","dickssportinggoods.com","dtlr.com","academy.com","nike.com","footlocker.co.uk","footlocker.de","footlocker.ca"]
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','data','W11_tranco_ranks.csv')
rows=[]
dates=[]
d=dt.date(2023,10,6)
while d<=dt.date(2026,10,6):
    dates.append(d); d=(d.replace(day=1)+dt.timedelta(days=32)).replace(day=6)
for d in dates:
    try:
        meta=requests.get(f"https://tranco-list.eu/api/lists/date/{d}",timeout=30).json()
        lid=meta['list_id']
        txt=requests.get(f"https://tranco-list.eu/download/{lid}/200000",timeout=120).text
        rk={}
        for line in txt.splitlines():
            r,dom=line.split(',',1)
            if dom in DOM: rk[dom]=int(r)
        rows.append({'date':str(d),'list':lid,**{k:rk.get(k) for k in DOM}}); print(d,lid,rk.get('footlocker.com'),rk.get('champssports.com'),flush=True)
    except Exception as e: print(d,'ERR',e)
    time.sleep(2)
with open(OUT,'w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['date','list']+DOM); w.writeheader(); w.writerows(rows)
