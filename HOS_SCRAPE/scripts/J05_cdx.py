import requests,json,sys
H={'User-Agent':'Research palazzolojustin@gmail.com'}
for u in ['jobs.dickssportinggoods.com*','dickssportinggoods.wd1.myworkdayjobs.com*','careers.dickssportinggoods.com*','jobs.dicks.com*']:
    try:
        r=requests.get('https://web.archive.org/cdx/search/cdx',params={'url':u,'output':'json','limit':30,'filter':'statuscode:200','collapse':'urlkey'},headers=H,timeout=60)
        j=r.json(); print(u,len(j)-1); 
        for x in j[1:12]: print('  ',x[1],x[2][:110])
    except Exception as e: print(u,'ERR',e)
