import requests,re,time,csv,sys
from bs4 import BeautifulSoup
# (hos_store, state, city slugs to check, open date)
EV=[(1500,'ny',['victor','farmington','canandaigua'],'2021-04-09'),(1372,'tn',['knoxville'],'2021-05-19'),
(1514,'mn',['minnetonka','hopkins','plymouth'],'2022-06-03'),(1587,'tx',['houston','webster','friendswood','katy','pearland'],'2023-05-15'),
(1582,'ia',['davenport'],'2023-07-21'),(1584,'ny',['latham','albany','colonie'],'2023-07-28'),(1581,'nc',['fayetteville'],'2023-07-28'),
(1546,'ny',['johnson-city','vestal','binghamton'],'2023-08-18'),(1580,'va',['chesapeake'],'2023-08-18'),(1583,'il',['champaign'],'2023-08-18'),
(1579,'pa',['scranton','dickson-city'],'2023-08-18'),(1548,'pa',['pittsburgh'],'2024-04-05'),(1536,'ma',['boston'],'2024-04-19'),
(1593,'de',['wilmington'],'2024-10-11'),(1572,'fl',['tampa'],'2024-10-18'),(1592,'ok',['oklahoma-city'],'2024-10-04'),(1620,'ok',['tulsa'],'2024-11-08'),
(1561,'nh',['salem'],'2024-11-15'),(1571,'fl',['miami'],'2025-02-12'),(1601,'oh',['beavercreek','dayton'],'2025-03-07'),(1611,'la',['baton-rouge'],'2025-05-16'),
(1666,'oh',['columbus'],'2025-08-15'),(1619,'tx',['dallas'],'2025-09-10'),(1623,'ks',['leawood','overland-park'],'2025-09-12'),(1567,'nj',['jersey-city'],'2025-09-18'),
(1607,'nc',['durham'],'2025-10-10'),(1602,'tx',['san-antonio','live-oak'],'2025-10-15'),(1594,'az',['glendale'],'2025-10-20'),(1665,'va',['charlottesville'],'2025-10-31'),
(1569,'oh',['strongsville'],'2025-10-31'),(1574,'nj',['freehold'],'2025-11-01'),(1633,'fl',['brandon'],'2025-11-07'),(1664,'ga',['kennesaw'],'2025-11-07'),
(1647,'al',['mobile'],'2025-10-15'),(1565,'ny',['amherst','buffalo'],'2026-03-13'),(1568,'ia',['cedar-rapids'],'2026-06-03')]
H={'User-Agent':'Mozilla/5.0 Research palazzolojustin@gmail.com'}
def parse(html):
    s=BeautifulSoup(html,'lxml')
    for x in s(['script','style']): x.decompose()
    t=s.get_text(' ',strip=True)
    if 'Click on Store Details' not in t: return None
    seg=t.split('Click on Store Details for Hours and More Information')[-1]
    seg=seg.split('Store Hours')[0] if False else seg
    stores=re.findall(r"(DICK'?s? Sporting Goods|Golf Galaxy|Going,? Going,? Gone!?|Field & Stream|Public Lands|House of Sport)[^A-Za-z0-9]*([^|]*?)(?= PHONE| DICK| Golf| Going| Field| Public|$)",seg,flags=re.I)
    return re.sub(r'PHONE:.*?Details','|',seg)[:600]
def get(u,tries=2):
    for i in range(tries):
        try:
            r=requests.get(u,headers=H,timeout=45,allow_redirects=True)
            if r.status_code==200: return r.text
            if r.status_code==429: time.sleep(10)
        except Exception as e: pass
        time.sleep(2)
    return None
out=[]
for hs,st,cities,od in EV:
    y,m,d=od.split('-'); 
    pre=f"{int(y)-(0 if int(m)>6 else 1)}{(int(m)-6)%12 or 12:02d}01" # ~6 months before
    pre=(__import__('datetime').date.fromisoformat(od)-__import__('datetime').timedelta(days=200)).strftime('%Y%m%d')
    for c in cities:
        u=f"https://stores.dickssportinggoods.com/{st}/{c}/"
        now=get(u); time.sleep(0.5)
        old=get(f"https://web.archive.org/web/{pre}id_/{u}"); time.sleep(3)
        pn=parse(now) if now else None; po=parse(old) if old else None
        out.append((hs,c,od,pre,po,pn))
        print(hs,c,od,'PRE',(po or 'NA')[:300],'|| NOW',(pn or 'NA')[:300],flush=True)
import json; json.dump(out,open('raw/J13/citypages.json','w'))
