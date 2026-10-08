import json,csv,datetime as dt,statistics as st,collections,sys
R='/home/user/dks-research/FL_INVENTORY_SCRAPE/'
def sale_of(fac):
    for k,v in (fac or {}).items():
        if k.lower() in('miscellaneous','misc'):
            for n in('Sale Product','Sale'):
                if n in v: return v[n]
    return None
rows={}
def add(dom,path,ts,pag,fac,prods,src):
    date=ts[:8]; key=(dom,path,date)
    if not pag: return
    tot=pag.get('totalResults'); sale=sale_of(fac)
    dep=[];sv=0;nv=0
    for p in prods or []:
        for v in p['v']:
            if v[0] and v[1] is not None:
                nv+=1
                if v[1]<v[0]-0.005: sv+=1; dep.append(1-v[1]/v[0])
    new1=new2=nd=0
    for p in prods or []:
        ds=[v[3][:10] for v in p['v'] if v[3] and v[3][:4]>'1950']
        if ds:
            nd+=1; f=min(ds)
            new1+= f>'2025-09-08'; new2+= f>'2026-07-01'
    rows[key]=dict(dom=dom,path=path,date=date,total=tot,sale_facet=sale if sale is not None else '',sale_share=round(sale/tot,4) if sale is not None and tot else '',
        p1_variant_sale_share=round(sv/nv,3) if nv else '',p1_variant_depth=round(st.mean(dep),3) if dep else '',p1_n=len(prods or []),p1_dated=nd,
        p1_new_after_20250908=round(new1/nd,3) if nd else '',p1_new_after_20260701=round(new2/nd,3) if nd else '',source=src)
for l in open(R+'raw/W03/snap_parsed.jsonl'):
    r=json.loads(l)
    if 'pag' not in r or not r['pag']: continue
    dom,path=r['target'].split('/',1); add(dom,'/'+path,r['ts'],r['pag'],r['facets'],r.get('prods'),'W03')
for l in open(R+'raw/V1/snaps.jsonl'):
    r=json.loads(l)
    if 'pag' not in r: continue
    add(r['dom'],r['path'],r['ts'],r['pag'],r['facets'],r.get('prods'),'V1')
# live
for p in json.load(open(R+'raw/V1/live_pages.json')):
    key=(p['dom'],p['path'],'20261008')
    rows[key]=dict(dom=p['dom'],path=p['path'],date='20261008',total=p['total'],sale_facet=p['sale'] or '',sale_share=p['share'],source='V1_live')
out=sorted(rows.values(),key=lambda r:(r['dom'],r['path'],r['date']))
# drop W03-flagged anomalies
bad={('footlocker.com','/category/mens/shoes.html','20241116'),('footlocker.com','/category/mens/shoes.html','20250209'),('footlocker.com','/category/sale.html','20260716')}
out=[r for r in out if (r['dom'],r['path'],r['date']) not in bad and r['total'] and r['total']>=100]
keys=['dom','path','date','total','sale_facet','sale_share','p1_variant_sale_share','p1_variant_depth','p1_n','p1_dated','p1_new_after_20250908','p1_new_after_20260701','source']
w=csv.DictWriter(open(R+'data/V1_timeseries.csv','w',newline=''),fieldnames=keys);w.writeheader();w.writerows(out)
print(len(out),'rows; V1-only',sum(1 for r in out if r['source']!='W03'))
SER={'FL_mens_shoes':('footlocker.com','/category/mens/shoes.html'),'FL_womens_shoes':('footlocker.com','/category/womens/shoes.html'),'FL_kids_shoes':('footlocker.com','/category/kids/shoes.html'),'FL_all_shoes':('footlocker.com','/category/shoes.html'),'FL_sale_page':('footlocker.com','/category/sale.html'),
 'CH_mens_shoes':('champssports.com','/category/mens/shoes.html'),'CH_all_shoes':('champssports.com','/category/shoes.html'),'CH_sale_page':('champssports.com','/category/sale.html'),
 'KFL_kids_shoes':('kidsfootlocker.com','/category/kids/shoes.html'),'KFL_shoes':('kidsfootlocker.com','/category/shoes.html'),'KFL_sale_page':('kidsfootlocker.com','/category/sale.html'),
 'CA_mens_shoes':('footlocker.ca','/category/mens/shoes.html'),'CA_all_shoes':('footlocker.ca','/category/shoes.html'),'CA_sale_page':('footlocker.ca','/category/sale.html')}
by={}
for r in out:
    for s,(d,p) in SER.items():
        if r['dom']==d and r['path']==p: by.setdefault(s,[]).append(r)
def wk(date): d=dt.datetime.strptime(date,'%Y%m%d').date(); return d-dt.timedelta(days=d.weekday())
def mean(L): return sum(L)/len(L) if L else None
print('series, n captures, first, last')
for s,L in by.items(): print(s,len(L),L[0]['date'],L[-1]['date'], 'n>=2025-08:',sum(1 for r in L if r['date']>='20250801'))
def window(L,a,b): return [r for r in L if a<=r['date']<=b]
Q={'Q3FY25 (8/3-11/1/25)':('20250803','20251101'),'Aug-Oct25':('20250801','20251031'),'Nov-Dec25 (Q4 bench)':('20251102','20251231'),'Q3FY26 (8/2-10/8/26)':('20260802','20261031'),'Q1FY26(2/1-5/2/26)':('20260201','20260502'),'Q2FY26 (5/3-8/1/26)':('20260503','20260801')}
print('\nQUARTER AVERAGES (mean of captures): total | sale_facet | mean sale share | share=sum/sum | n')
tabq=[]
for s,L in by.items():
    for q,(a,b) in Q.items():
        W=window(L,a,b)
        sh=[r['sale_share'] for r in W if r['sale_share']!='']
        if W: 
            ss=sum(r['sale_facet'] for r in W if r['sale_facet']!='')/max(1,sum(r['total'] for r in W if r['sale_facet']!=''))
            tabq.append((s,q,round(mean([r['total'] for r in W])),round(mean([r['sale_facet'] for r in W if r['sale_facet']!='']) or 0) if sh else '',round(mean(sh),3) if sh else '',len(W)))
for t in tabq: print(*t,sep=' | ')
json.dump(tabq,open(R+'raw/V1/quarter_table.json','w'))
print('\nWEEKLY (week start Mon): share%/total, 2025-07..2026-10 for core series')
core=['FL_mens_shoes','FL_all_shoes','FL_sale_page','CH_mens_shoes','KFL_kids_shoes','CA_mens_shoes']
W={}
for s in core:
    for r in by.get(s,[]):
        if r['date']>='20250701':
            W.setdefault(wk(r['date']),{}).setdefault(s,[]).append(r)
print('week',*core,sep='\t')
for k in sorted(W):
    cells=[]
    for s in core:
        L=W[k].get(s)
        if not L: cells.append('-');continue
        if s.endswith('sale_page'): cells.append(str(round(mean([r['total'] for r in L]))))
        else:
            sh=[r['sale_share'] for r in L if r['sale_share']!='']
            cells.append(f"{100*mean(sh):.1f}%/{round(mean([r['total'] for r in L]))}" if sh else f"-/{round(mean([r['total'] for r in L]))}")
    print(k,*cells,sep='\t')
