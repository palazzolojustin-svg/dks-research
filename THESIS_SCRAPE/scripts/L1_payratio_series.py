"""L1: build DKS pay-ratio / workforce series from DEF 14A proxies (raw/L1_proxy_*.txt fetched by L1_proxies.py).
Rerun: python THESIS_SCRAPE/scripts/L1_payratio_series.py -> raw/L1_payratio_series.csv
Values transcribed from the proxy text (verified by regex print in L1 session 2026-10-07).
"""
import csv
rows=[
# fiscal yr, proxy date, determination date, FT, PT, temp, median all $, median emp role, median hrs/wk, median FT $, median FT role
('FY2017','2018-05-02','2017-11-06',14832,26363,4764,9885,'PT Bikes & Fitness Sales Associate',24,35049,'Freight Flow Sales Leader'),
('FY2018','2019-05-01','2019-02-02',15119,24204,1324,10091,'PT Customer Service Specialist',18,36288,'Apparel Sales Lead'),
('FY2019','2020-04-29','2020-02-01',15229,24806,1497,10120,'PT Footwear Sales Associate (28 wks)',32,37595,'Bicycle Technician'),
('FY2020','2021-04-28','2021-01-30',16754,32532,774,10440,'PT Footwear Sales Associate',18,36046,'Customer Service Specialist'),
('FY2021','2022-05-06','2022-01-29',17717,30350,2671,10495,'PT Apparel Sales Associate',16,37281,'Freight Flow Lead'),
('FY2022','2023-05-05','2023-01-28',18720,32432,1572,10585,'PT Apparel Sales Associate',13,39906,'Store Sales Leader'),
('FY2023','2024-05-02','2024-02-03',18845,35238,1391,11353,'PT Retail Cashier',17,43157,'Retail Loss Prevention Lead'),
('FY2024','2025-05-02','2025-02-01',18507,37507,0,11513,'PT Retail Operations Associate',13,44489,'Retail Apparel Sales Lead'),
('FY2025','2026-05-01','2026-01-31',18963,40787,0,11259,'PT Retail Sales Associate',12,46524,'Retail Freight Flow Lead'),
]
out=[]
prev=None
for r in rows:
    fy,pd,dd,ft,pt,tmp,med,role,hrs,medft,ftrole=r
    tot=ft+pt+tmp
    d=dict(fy=fy,proxy=pd,date=dd,ft=ft,pt=pt,temp=tmp,total=tot,ft_share=round(ft/tot*100,1),median_all=med,median_role=role,median_hrs_wk=hrs,
           median_ft=medft,median_ft_role=ftrole)
    if prev:
        d['total_yoy%']=round((tot/prev['total']-1)*100,1); d['ft_yoy%']=round((ft/prev['ft']-1)*100,1); d['pt_yoy%']=round((pt/prev['pt']-1)*100,1)
        d['median_ft_yoy%']=round((medft/prev['median_ft']-1)*100,1); d['median_all_yoy%']=round((med/prev['median_all']-1)*100,1)
    out.append(d); prev=d
keys=list(out[-1].keys())
with open(r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\L1_payratio_series.csv','w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=keys); w.writeheader(); [w.writerow(x) for x in out]
for x in out: print({k:x.get(k) for k in ['fy','ft','pt','total','ft_share','total_yoy%','pt_yoy%','median_all','median_all_yoy%','median_hrs_wk','median_ft','median_ft_yoy%']})
# FY17->FY25 CAGR of median FT
print('median FT CAGR FY17-25', round(((46524/35049)**(1/8)-1)*100,2), ' FY22-25', round(((46524/39906)**(1/3)-1)*100,2))
