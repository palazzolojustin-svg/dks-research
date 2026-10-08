import csv,requests,re,time,os
H={"User-Agent":"Research palazzolojustin@gmail.com"}
rows=[r for r in csv.DictReader(open("data/M05_fts_hits.csv")) if r["form"] in("FWP","424B2","424H","424B5","424B3","424B4")]
print(len(rows))
out=[]
for r in rows:
  acc,fn=r["id"].split(":");url=f"https://www.sec.gov/Archives/edgar/data/{int(r['cik'])}/{acc.replace('-','')}/{fn}"
  p="raw/M05/"+acc+"_"+fn
  if not os.path.exists(p):
    try:
      t=requests.get(url,headers=H,timeout=60).text;open(p,"w").write(t);time.sleep(.15)
    except Exception as e: print(e);continue
  t=open(p).read()
  n=len(re.findall(r"Foot Locker|Champs|FOOT LOCKER",t))
  out.append((r["file_date"],r["form"],r["filer"],n,url))
w=csv.writer(open("data/M05_docs.csv","w"));w.writerow("date form filer nFL url".split());w.writerows(out)
print(sum(1 for o in out if o[3]>0))
