import requests,csv,time
H={'User-Agent':'Research palazzolojustin@gmail.com'}
stores={'1548':'Ross Park','1536':'Boston','1593':'Wilmington','1572':'Tampa','1592':'OKC','1620':'Tulsa','1561':'Salem NH'}
rows=[]
for s,n in stores.items():
    for pre in ['dickssportinggoods.wd1.myworkdayjobs.com/*/job/%05d*'%int(s),'dickssportinggoods.wd1.myworkdayjobs.com/*/job/%04d*'%int(s)]:
        r=requests.get('https://web.archive.org/cdx/search/cdx',params={'url':pre,'output':'json','fl':'timestamp,original,statuscode','collapse':'urlkey'},headers=H,timeout=90)
        try: j=r.json()
        except: print(s,'bad',r.status_code); continue
        print(s,n,pre[-12:],len(j)-1)
        for x in j[1:]: rows.append([s,n]+x)
        time.sleep(.5)
csv.writer(open('data/J05_cdx_jobs.csv','w')).writerows([['store','name','ts','url','status']]+rows)
for r in rows[:60]: print(r[0],r[2],r[3][60:170])
