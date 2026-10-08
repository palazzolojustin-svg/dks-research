"""J06: live Workday CXS census of 'House of Sport' location-type postings + details (startDate). Output raw/J06/hos_postings.jsonl"""
import requests,json,time,re,html,os
BASE='https://dickssportinggoods.wd1.myworkdayjobs.com/wday/cxs/dickssportinggoods/DSG'
H={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64) AppleWebKit/537.36 Chrome/124 Safari/537.36','Content-Type':'application/json','Accept':'application/json'}
LT='CF_-_Job_Posting_Location_Type__LRV__Extended'
s=requests.Session()
def post(f,off=0):
    for a in range(6):
        try:
            r=s.post(BASE+'/jobs',headers=H,json={"appliedFacets":f,"limit":20,"offset":off,"searchText":""},timeout=40)
            if r.status_code==200: return r.json()
        except Exception as e: pass
        time.sleep(2+3*a)
    raise RuntimeError
d=post({})
lt=None
for f in d['facets']:
    for v in f.get('values',[]):
        if 'values' in v:
            for w in v['values']:
                if w.get('descriptor')=='House of Sport' and v['facetParameter']==LT: lt=w['id']
        elif f.get('facetParameter')==LT and v.get('descriptor')=='House of Sport': lt=v['id']
print('lt',lt)
rows={};off=0
while True:
    d=post({LT:[lt]},off); jp=d.get('jobPostings',[])
    if not jp: break
    for j in jp: rows[j['externalPath']]=j
    off+=20; time.sleep(.3)
print(len(rows))
out=open('raw/J06/hos_postings.jsonl','w')
for i,(p,j) in enumerate(rows.items()):
    rec={'path':p,'title':j.get('title'),'loc':j.get('locationsText'),'postedOn':j.get('postedOn')}
    for a in range(4):
        try:
            x=s.get(BASE+p,headers=H,timeout=40)
            if x.status_code==200:
                ji=x.json().get('jobPostingInfo',{})
                desc=re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',ji.get('jobDescription','') or '')))
                rec.update(req=ji.get('jobReqId'),start=ji.get('startDate'),tt=ji.get('timeType'),loc2=ji.get('location'),desc=desc[:1500]);break
        except Exception: pass
        time.sleep(2)
    out.write(json.dumps(rec)+'\n'); time.sleep(.2)
