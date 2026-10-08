import pandas as pd
a=pd.read_csv('raw/W11/gt_v4a.csv',index_col=0,parse_dates=True)
b=pd.read_csv('raw/W11/gt_v4b.csv',index_col=0,parse_dates=True)
a['kids foot locker']=b['kids foot locker'];a['nike']=b['nike']
a.to_csv('data/V4_trends.csv')
m=a.resample('MS').mean().round(2)
y=(m/m.shift(12)-1)*100
print(m.loc['2025-06':].to_string())
print(y.loc['2025-01':].round(0).to_string())
# FL relative to comparators
r=pd.DataFrame({'FL/JD':m['foot locker']/m['jd sports'],'FL/FinishLine':m['foot locker']/m['finish line'],'FL/DKS':m['foot locker']/m['dicks sporting goods'],'FL/Champs':m['foot locker']/m['champs sports']})
print(r.loc['2025-06':].round(2).to_string())
for lab,s,e in [('Aug-Oct','08','10')]:
  for yr in (2025,2026):
    x=a.loc[f'{yr}-{s}-01':f'{yr}-{e}-07']; print(yr,x.mean().round(2).to_dict())
