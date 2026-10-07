"""R3: EDGAR FTS for target malls (2025-07+ , all forms) to find surveillance/10-D/new deals that may print DKS/HoS sales.
Rerun: python R3_fts_malls.py -> raw/R3/R3_fts_malls.csv"""
import requests, time, csv, re
H={"User-Agent":"IndependentResearch research-script palazzolojustin@gmail.com"}
Q=['"Ridgedale"','"Empire Mall"','"Cape Cod Mall"','"Shops at Mission Viejo"','"Hamburg Pavilion"','"Crossgates"','"International Plaza"','"Freehold Raceway"','"Washington Square" "Tigard"','"5th Street Station"','"Westroads"','"Mall of Victor Valley"','"Galleria at Sunset"','"Oakdale Commons"','"Newport Centre"','"Northshore Mall"','"Brandon Exchange"','"House of Sport"']
rows=[]
for q in Q:
    frm=0
    while True:
        d={}
        for k in range(5):
            try:
                r=requests.get("https://efts.sec.gov/LATEST/search-index",params={"q":q,"dateRange":"custom","startdt":"2025-07-01","enddt":"2026-10-07","from":frm},headers=H,timeout=60); d=r.json()
                if "hits" in d: break
            except Exception as e: print("exc",e)
            time.sleep(3*(k+1))
        hh=d.get("hits",{}).get("hits",[])
        for x in hh:
            s=x["_source"]; adsh,fn=x["_id"].split(":",1)
            rows.append([q,s.get("file_date"),s.get("form"),(s.get("display_names") or [""])[0][:60],f"https://www.sec.gov/Archives/edgar/data/{s['ciks'][0].lstrip('0')}/{adsh.replace('-','')}/{fn}"])
        frm+=len(hh)
        if not hh or frm>=d["hits"]["total"]["value"] or frm>=500: break
        time.sleep(0.3)
    print(q,frm,flush=True)
with open(r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\R3\R3_fts_malls.csv","w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["q","date","form","filer","url"]); w.writerows(rows)
