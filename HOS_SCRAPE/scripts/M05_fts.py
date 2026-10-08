import requests,json,time,csv,itertools
H={"User-Agent":"Research palazzolojustin@gmail.com"}
qs=['"Foot Locker" "Sales PSF"','"Foot Locker" "Occupancy Cost"','"Champs Sports" "Sales PSF"','"Kids Foot Locker" "Sales"','"Foot Locker" "Largest Tenants" "Sales"','"Champs Sports" "Occupancy Cost"','"Foot Locker" "In-line Sales"']
forms="FWP,424B2,424H,424B5,424B3,424B4"
rows={}
for q in qs:
  for yr in range(2019,2027):
    for f in (forms,None):
      p={"q":q,"dateRange":"custom","startdt":f"{yr}-01-01","enddt":f"{yr}-12-31"}
      if f:p["forms"]=f
      for frm in (0,100,200):
        try:r=requests.get("https://efts.sec.gov/LATEST/search-index",params=p|{"from":frm},headers=H,timeout=30).json()
        except Exception as e: print(q,yr,e);break
        hits=r.get("hits",{}).get("hits",[])
        for h in hits:
          s=h["_source"];i=h["_id"]
          if s["form"] in("FWP","424B2","424H","424B5","424B3","424B4","ABS-15G","8-K","10-D","10-K"):
            rows[i]=(s["file_date"],s["form"],s["display_names"][0][:60],i)
        time.sleep(.2)
        if len(hits)<100:break
w=csv.writer(open("data/M05_fts_hits.csv","w"));w.writerow("file_date form filer id".split())
for v in sorted(rows.values()):w.writerow(v)
print(len(rows))
import collections;print(collections.Counter(v[1] for v in rows.values()))
