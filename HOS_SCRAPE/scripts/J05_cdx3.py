import requests,csv,time,re,sys
H={'User-Agent':'Research palazzolojustin@gmail.com'}
def get(params,tries=4):
    for i in range(tries):
        try:
            r=requests.get('https://web.archive.org/cdx/search/cdx',params=params,headers=H,timeout=180)
            return r.json()
        except Exception as e:
            time.sleep(3)
    return None
tot=[]
for base in ['dickssportinggoods.wd1.myworkdayjobs.com/DSG/job/','dickssportinggoods.wd1.myworkdayjobs.com/C-DSG/job/','dickssportinggoods.wd1.myworkdayjobs.com/en-US/DSG/job/']:
    j=get({'url':base+'*','output':'json','fl':'timestamp,original,statuscode','collapse':'urlkey','limit':200000})
    print(base,None if j is None else len(j)-1); 
    if j: tot+=j[1:]
csv.writer(open('data/J05_wd_all.csv','w')).writerows([['ts','url','status']]+tot)
from collections import Counter
c=Counter()
for ts,u,s in tot:
    m=re.search(r'/job/(\d{4,5})-([^/]+)/',u)
    c[(m.group(1),m.group(2)) if m else ('other','')]+=1
print(len(c)); print([k for k in c if k[0] in ('01548','01536','01593','01572','01592','01620','01561','1548','1536','1593','1572','1592','1620','1561')])
print(c.most_common(15))
