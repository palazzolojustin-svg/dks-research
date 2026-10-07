import requests, re, time, os
H={'User-Agent':'Mozilla/5.0 (research; palazzolojustin@gmail.com)'}
def get(u):
    for a in range(8):
        try:
            r=requests.get(u,headers=H,timeout=60)
            if r.status_code==200: return r
        except Exception as e: pass
        time.sleep(6)
def save(u,fn):
    f=get(u)
    if f is not None: open(fn,'wb').write(f.content); print('saved',fn,len(f.content),flush=True)
    else: print('fail',u,flush=True)
save('https://www.revenue.state.mn.us/sites/default/files/2021-04/MINNETONKA%20CITY%20BY%20INDUSTRY%202019.xlsx','raw/B5_mn/minnetonka_2019.xlsx')
save('https://www.revenue.state.mn.us/sites/default/files/2026-06/minnetonka-city-industry-2024.xlsx','raw/B5_mn/minnetonka_2024.xlsx')
for y in [2021,2022,2023]:
    r=get(f'https://www.revenue.state.mn.us/{y}-sales-and-use-tax-revenue-city')
    if r is None: print(y,'page fail'); continue
    ls=[l for l in set(re.findall(r'href="([^"#]+)"',r.text)) if 'minnetonka' in l.lower()]
    print(y,ls,flush=True)
    for l in ls: save(l if l.startswith('http') else 'https://www.revenue.state.mn.us'+l, f'raw/B5_mn/minnetonka_{y}.xlsx')
