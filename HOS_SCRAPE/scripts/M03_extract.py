import csv,re,os,collections
from bs4 import BeautifulSoup
rows=list(csv.DictReader(open('data/M03_fts_hits.csv')))
seen=set();out=[]
for r in rows:
    fn='raw/M03/'+re.sub(r'\W','_',r['url'][-60:])
    if not os.path.exists(fn): continue
    t=BeautifulSoup(open(fn).read(),'lxml').get_text(' ');t=re.sub(r'\s+',' ',t)
    for m in re.finditer(r"(?i)dick.s (sporting goods|house of sport)|House of Sport",t):
        s=t[max(0,m.start()-150):m.end()+350]
        if not re.search(r'(?i)sales|\$\d',s): continue
        if r['mall'].split()[0].lower() not in t[:200000].lower(): continue
        k=(r['city'],re.sub(r'\W','',s)[:120])
        if k in seen: continue
        seen.add(k); out.append((r['city'],r['date'],r['form'],r['url'].split('/')[-3]+'/'+r['url'].split('/')[-2],s))
import pickle;pickle.dump(out,open('raw/M03/out.pkl','wb'))
c=collections.Counter(o[0] for o in out);print(c)
