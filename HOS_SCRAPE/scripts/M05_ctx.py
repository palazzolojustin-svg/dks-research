import re,os,csv
meta={}
for r in csv.DictReader(open("data/M05_docs.csv")):
  u=r["url"].split("/");meta[u[-2]+"_"+u[-1]]=r
out=[]
for f in sorted(os.listdir("raw/M05")):
  r=meta.get(f.replace("-","",2))
  if not r: continue
  t=open("raw/M05/"+f).read()
  t=re.sub(r"<[^>]+>"," ",t);t=re.sub(r"&nbsp;|&#160;"," ",t);t=re.sub(r"\s+"," ",t)
  for m in re.finditer(r"(Foot Locker|Champs|FOOT LOCKER)",t):
    c=t[max(0,m.start()-250):m.end()+350]
    if re.search(r"[Ss]ales",c) and re.search(r"\$\s?\d",c):
      out.append((r["date"],r["filer"][:40],f,c))
print(len(out))
seen=set()
for d,fl,f,c in out:
  k=c[200:330]
  if k in seen: continue
  seen.add(k)
  print(d,fl,f[:40],"|",c);print()
