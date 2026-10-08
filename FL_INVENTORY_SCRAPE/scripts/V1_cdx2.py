import json,subprocess,concurrent.futures as cf
CA='/root/.ccr/ca-bundle.crt'
F='/home/user/dks-research/FL_INVENTORY_SCRAPE/raw/V1/cdx_all.json'
jobs=[]
wins=[('2024','202406'),('202407','202412'),('2025','202506'),('202507','202509'),('202510','202512'),('2026','202606'),('202607','2026')]
for d,p in [('footlocker.com','category/sale.html*'),('footlocker.com','category/mens/shoes.html*'),('footlocker.com','category/womens/shoes/*'),('footlocker.ca','category/sale.html*'),('footlocker.ca','category/mens/shoes.html*')]:
    for a,b in wins: jobs.append((d,p,a,b))
def q(j):
    d,p,a,b=j
    u=f'https://web.archive.org/cdx/search/cdx?url=www.{d}/{p}&output=txt&from={a}&to={b}&filter=statuscode:200&fl=timestamp,original&collapse=timestamp:8'
    for i in range(5):
        r=subprocess.run(['curl','-sS','--cacert',CA,'-m','120',u],capture_output=True,text=True)
        if r.returncode==0: break
    return d,p,a,[l.split(' ',1) for l in r.stdout.splitlines() if ' ' in l],r.stderr[:40]
c=json.load(open(F))
with cf.ThreadPoolExecutor(4) as ex:
    for d,p,a,rows,e in ex.map(q,jobs):
        c.setdefault(d,[]).extend(rows); print(d,p,a,len(rows),e,flush=True)
json.dump(c,open(F,'w'))
