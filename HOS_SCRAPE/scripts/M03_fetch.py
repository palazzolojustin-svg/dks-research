import requests,csv,re,os,time,concurrent.futures as cf
H={'User-Agent':'Research palazzolojustin@gmail.com'}
rows=list(csv.DictReader(open('data/M03_fts_hits.csv')))
def get(r):
    u=r['url']; fn='raw/M03/'+re.sub(r'\W','_',u[-60:])
    if os.path.exists(fn): return
    for i in range(3):
        try:
            t=requests.get(u,headers=H,timeout=60).text; open(fn,'w').write(t); time.sleep(.3); return
        except Exception as e: time.sleep(2)
with cf.ThreadPoolExecutor(4) as ex: list(ex.map(get,rows))
print(len(os.listdir('raw/M03')))
