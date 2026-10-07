import json, re, os, sys, time, gzip, requests
site=sys.argv[1]; cdx=sys.argv[2]; outdir=sys.argv[3]; per_month=int(sys.argv[4]) if len(sys.argv)>4 else 3
os.makedirs(outdir,exist_ok=True)
d=json.load(open(cdx))[1:]
pat=re.compile(r'release-dates(\.html|/|-new\.html)?(\?.*)?$')
d=[x for x in d if pat.search(x[1]) and x[0]>='2024']
bymonth={}
for x in sorted(d):
    bymonth.setdefault(x[0][:6],[]).append(x)
sel=[]
for m,xs in sorted(bymonth.items()):
    # pick spread by day: distinct days, evenly spaced
    days={}
    for x in xs: days.setdefault(x[0][:8],x)
    xs=list(days.values())
    if len(xs)<=per_month: sel+=xs
    else:
        step=len(xs)/per_month
        sel+=[xs[int(i*step)] for i in range(per_month)]
print(len(sel),'snapshots')
s=requests.Session()
for ts,url,_,_ in sel:
    fn=f'{outdir}/{site}_{ts}.html'
    if os.path.exists(fn) and os.path.getsize(fn)>10000: continue
    for a in range(4):
        try:
            r=s.get(f'https://web.archive.org/web/{ts}id_/{url}',timeout=60)
            b=r.content
            if b[:2]==b'\x1f\x8b': b=gzip.decompress(b)
            open(fn,'wb').write(b); print(ts,r.status_code,len(b),flush=True); break
        except Exception as e:
            print('err',ts,e,flush=True); time.sleep(5*(a+1))
    time.sleep(1.5)
