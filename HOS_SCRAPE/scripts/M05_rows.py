import re,os,csv,json
meta={}
for r in csv.DictReader(open("data/M05_docs.csv")):
  u=r["url"].split("/");meta[u[-2]+"_"+u[-1]]=r
pat=re.compile(r"((?:Kids )?Foot Locker(?:/[A-Za-z ]+)?|Champs(?: Sports)?|Footaction|Lady Foot Locker|Foot Locker/Lady Foot Locker)\s*((?:\$[\d,]+\s+\$[\d,]+\s*){1,4})(\d+\.\d+\s*%)?")
rows=[];seen=set()
for f in sorted(os.listdir("raw/M05")):
  r=meta.get(f.replace("-","",2))
  if not r or any(x in r["filer"] for x in("DICK","Grow","CBL")): continue
  t=open("raw/M05/"+f).read()
  t=re.sub(r"<[^>]+>"," ",t);t=re.sub(r"&nbsp;|&#160;|&#8194;|&#8201;"," ",t);t=re.sub(r"\s+"," ",t)
  for m in pat.finditer(t):
    key=(m.group(0),r["date"][:4])
    hdr=t[max(0,m.start()-900):m.start()]
    yrs=re.findall(r"(?:TTM|T-12|Trailing|FY|\b)(?:\s?\d{1,2}/\d{1,2}/)?(20\d\d)",hdr)[-4:]
    pr=re.findall(r"(?:Tenant Sales|Sales PSF|Sales \(\$ ?PSF\)|Sales \$)",hdr)
    rows.append(dict(date=r["date"],filer=r["filer"][:35],file=f[-40:],tenant=m.group(1),vals=m.group(2).strip(),occ=m.group(3) or "",yrs=",".join(yrs),hdr=hdr[-300:]))
import pandas as pd
d=pd.DataFrame(rows);d.to_csv("data/M05_rows.csv",index=False)
print(len(d));print(d.drop_duplicates(["vals","tenant"])[["date","filer","tenant","vals","occ","yrs"]].to_string(max_colwidth=75))
