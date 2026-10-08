import csv,re,os,collections,html
rows=list(csv.DictReader(open('data/M03_fts_hits.csv')))
seen=set();out=[]
for r in rows:
    fn='raw/M03/'+re.sub(r'\W','_',r['url'][-60:])
    if not os.path.exists(fn): continue
    t=open(fn,errors='ignore').read()
    t=re.sub(r'<[^>]+>',' ',t);t=html.unescape(t);t=re.sub(r'\s+',' ',t)
    mn=r['mall'].split()[0].lower()
    for m in re.finditer(r"(?i)dick.s (sporting goods|house of sport)|House of Sport",t):
        s=t[max(0,m.start()-150):m.end()+350]
        if not re.search(r'(?i)sales|\$\d',s): continue
        if mn not in t.lower(): continue
        k=(r['city'],re.sub(r'\W','',s)[:120])
        if k in seen: continue
        seen.add(k); out.append((r['city'],r['date'],r['form'],r['url'].split('/')[-3]+'/'+r['url'].split('/')[-2],s))
import pickle;pickle.dump(out,open('raw/M03/out.pkl','wb'))
print(len(out),collections.Counter(o[0] for o in out))
