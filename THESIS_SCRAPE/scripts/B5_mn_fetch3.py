import requests, re, time
H={'User-Agent':'Mozilla/5.0 (research; palazzolojustin@gmail.com)'}
def get(u):
    for a in range(8):
        try:
            r=requests.get(u,headers=H,timeout=60)
            if r.status_code==200: return r
        except Exception: pass
        time.sleep(6)
def save(u,fn):
    f=get(u)
    print(('saved' if f is not None else 'fail'),fn,flush=True)
    if f is not None: open(fn,'wb').write(f.content)
save('https://www.revenue.state.mn.us/sites/default/files/2023-07/mn-state-3-digit-industry-code-2021.xlsx','raw/B5_mn/state3_2021.xlsx')
save('https://www.revenue.state.mn.us/sites/default/files/2024-02/mn-state-3-digit-industry-code-2022.xlsx','raw/B5_mn/state3_2022.xlsx')
for p in ['/sales-and-use-tax-statistics-2023','/sales-and-use-tax-statistics-2024','/2023-sales-and-use-tax-revenue-city']:
    r=get('https://www.revenue.state.mn.us'+p)
    if r is None: print(p,'fail'); continue
    for l in set(re.findall(r'href="([^"#]+)"',r.text)):
        if ('3-digit' in l.lower() or 'minnetonka' in l.lower()):
            y='2023' if '2023' in l else ('2024' if '2024' in l else 'x')
            save(l if l.startswith('http') else 'https://www.revenue.state.mn.us'+l, 'raw/B5_mn/'+('state3_' if '3-digit' in l.lower() else 'minnetonka_')+y+'.xlsx')
