import requests,os,io,pandas as pd
H={'User-Agent':'Research palazzolojustin@gmail.com'}
out='raw/J03/'
for y,qs in [(2023,[1,2,3,4]),(2024,[1,2,3,4]),(2025,[1,2,3,4]),(2026,[1,2])]:
  for q in qs:
    for n in ('459110','451110'):
      if n=='451110' and y>=2023 and False: pass
      f=f'{out}ind{n}_{y}Q{q}.csv'
      if os.path.exists(f): continue
      r=requests.get(f'https://data.bls.gov/cew/data/api/{y}/{q}/industry/{n}.csv',headers=H,timeout=120)
      print(y,q,n,r.status_code,len(r.content))
      if r.status_code==200: open(f,'wb').write(r.content)
