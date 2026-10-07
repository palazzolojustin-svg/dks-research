import requests, pandas as pd
rows=requests.get('https://data.colorado.gov/resource/k3gg-hhc8.json',params={'$where':"naics='459' and city in('Glendale','Thornton','Denver','Lone Tree','Broomfield','Littleton','Aurora','Colorado Springs')",'$limit':50000},timeout=120).json()
d=pd.DataFrame(rows); d['ym']=d.year.astype(float).astype(int).astype(str)+'-'+d.month.str.zfill(2); d['v']=pd.to_numeric(d.retailsales)/1e6
d['n']=pd.to_numeric(d.numberofretailers)
p=d.pivot_table(index='ym',columns='city',values='v'); pn=d.pivot_table(index='ym',columns='city',values='n')
pd.set_option('display.width',250)
print(p.round(2).tail(40).to_string()); print(pn.tail(6).to_string())
d.to_csv('raw/B5_CO_naics459_cities.csv',index=False)
