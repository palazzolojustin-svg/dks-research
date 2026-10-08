import json,re,sys,time
from googlenewsdecoder import gnewsdecoder
import trafilatura, requests
d=json.load(open('raw/J09/gnews.json'))
kw=re.compile(r"House of Sport|HoS",re.I)
seen={};
for c,items in d.items():
    for t,l,p in items:
        if kw.search(t) and l not in seen and not re.search(r"shoot|theft|sentenc|arrest|death|police|CSRwire|Nationwide Celebration",t): seen[l]=(c,t,p)
print(len(seen))
res=[]
pat=re.compile(r"[^.]{0,200}\b(hir\w+|jobs?|employ\w+|teammates?|team members|associates|staff|workers|square[- ]f\w+|sq\.? ?ft)\b[^.]{0,200}\.",re.I)
for l,(c,t,p) in seen.items():
    try:
        r=gnewsdecoder(l,interval=0.3)
        u=r.get('decoded_url') if r.get('status') else None
        if not u: continue
        h=requests.get(u,timeout=20,headers={"User-Agent":"Mozilla/5.0"}).text
        tx=trafilatura.extract(h) or ''
    except Exception as e:
        continue
    sn=[m.group(0).strip() for m in pat.finditer(tx) if re.search(r"\d",m.group(0)) and re.search(r"hir|job|employ|teammate|team member|associate|staff|worker",m.group(0),re.I)]
    res.append(dict(city=c,title=t,date=p[5:16],url=u,snips=sn[:6]))
json.dump(res,open('raw/J09/articles.json','w'))
for x in res:
    if x['snips']:
        print('##',x['city'],x['date'],x['title'][:80],x['url'][:100])
        for s in x['snips']: print('   -',s[:380].replace('\n',' '))
