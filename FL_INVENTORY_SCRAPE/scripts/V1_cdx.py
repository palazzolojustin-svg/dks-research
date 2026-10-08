import json,subprocess,concurrent.futures as cf,sys
CA='/root/.ccr/ca-bundle.crt'
doms=['footlocker.com','champssports.com','kidsfootlocker.com','footlocker.ca']
paths=['category/sale.html*','category/sale/*','category/mens/shoes.html*','category/womens/shoes.html*','category/kids/shoes.html*','category/mens/shoes/*','category/womens/shoes/*','category/kids/shoes/*','category/mens/clothing.html*','category/womens/clothing.html*','category/brands/*','category/mens.html*','category/womens.html*','category/kids.html*','category/shoes.html*','category/boys*','category/girls*']
def q(a):
    d,p=a
    u=f'https://web.archive.org/cdx/search/cdx?url=www.{d}/{p}&output=txt&from=2024&to=2026&filter=statuscode:200&fl=timestamp,original&collapse=timestamp:8'
    for i in range(4):
        r=subprocess.run(['curl','-sS','--cacert',CA,'-m','150',u],capture_output=True,text=True)
        if r.returncode==0: break
    rows=[l.split(' ',1) for l in r.stdout.splitlines() if ' ' in l]
    return d,p,rows,r.stderr[:60]
out={}
with cf.ThreadPoolExecutor(5) as ex:
    for d,p,rows,e in ex.map(q,[(d,p) for d in doms for p in paths]):
        out.setdefault(d,[]).extend(rows); print(d,p,len(rows),e,flush=True)
json.dump(out,open('/home/user/dks-research/FL_INVENTORY_SCRAPE/raw/V1/cdx_all.json','w'))
