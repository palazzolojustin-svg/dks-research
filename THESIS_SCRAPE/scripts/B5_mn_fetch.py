import requests, re, time, os
H={'User-Agent':'Mozilla/5.0 (research; palazzolojustin@gmail.com)'}
def get(u):
    for a in range(5):
        try: return requests.get(u,headers=H,timeout=60)
        except Exception as e: time.sleep(5)
os.makedirs('raw/B5_mn',exist_ok=True)
for y in [2018,2019,2020,2021,2022,2023,2024]:
    r=get(f'https://www.revenue.state.mn.us/{y}-sales-and-use-tax-revenue-city')
    if r is None or r.status_code!=200: print(y,'page fail',None if r is None else r.status_code); continue
    ls=[l for l in set(re.findall(r'href="([^"#]+)"',r.text)) if 'minnetonka' in l.lower() or ('all' in l.lower() and 'cit' in l.lower() and 'xls' in l.lower())]
    print(y, ls)
    for l in ls:
        if 'minnetonka' in l.lower():
            u=l if l.startswith('http') else 'https://www.revenue.state.mn.us'+l
            f=get(u)
            if f is not None and f.status_code==200:
                fn=f'raw/B5_mn/minnetonka_{y}'+os.path.splitext(u)[1]
                open(fn,'wb').write(f.content); print('  saved',fn,len(f.content))
    time.sleep(1)
