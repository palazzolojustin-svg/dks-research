import re,os,csv
import pandas as pd
meta={}
for r in csv.DictReader(open("data/M05_docs.csv")):
  u=r["url"].split("/");meta[u[-2]+"_"+u[-1]]=r
tok=r"(?:\$[\d,]+(?:\.\d+)?|NAV|N/A|NA|\d+\.\d+\s?%|\d+\s?%|--)"
pat=re.compile(r"((?:Kids )?Foot ?Locker(?:\s?/\s?[A-Za-z ]{3,25}?)?|Champs(?: Sports)?|Footaction|Lady Foot Locker)\s*(?:\(\d\)\s*)?((?:"+tok+r"\s*){2,10})")
hp=re.compile(r"Loan No\.?\s*\d+\s*[-–]?\s*(.{3,70}?)\s*(?:Mortgage Loan Information|Cut-off Date|Original Balance|Property Information|Collateral Asset|Loan Information)")
rows=[];seen=set()
for f in sorted(os.listdir("raw/M05")):
  r=meta.get(f.replace("-","",2))
  if not r or any(x in r["filer"] for x in("DICK","Grow","CBL")): continue
  t=open("raw/M05/"+f).read()
  t=re.sub(r"<[^>]+>"," ",t);t=re.sub(r"&nbsp;|&#160;|&#8194;|&#8201;|&thinsp;|&#8202;"," ",t);t=re.sub(r"&rsquo;|&#8217;","'",t);t=re.sub(r"\s+"," ",t)
  heads=[(m.start(),m.group(1)) for m in hp.finditer(t)]
  for m in pat.finditer(t):
    if "$" not in m.group(2): continue
    prop=[h for p,h in heads if p<m.start()]
    prop=prop[-1] if prop else ""
    hdr=t[max(0,m.start()-700):m.start()]
    h=re.findall(r"((?:TTM|T-12|Trailing)[^$]{0,25}|20\d\d(?: Sales)?(?: \(?PSF\)?)?|Sales PSF|Occupancy Cost|Occ(?:upancy)? Cost)",hdr)[-9:]
    key=(m.group(1),m.group(2).strip(),prop)
    if key in seen: continue
    seen.add(key)
    rows.append(dict(date=r["date"],form=r["form"],trust=r["filer"][:32],prop=prop[:45],tenant=m.group(1).strip(),vals=m.group(2).strip(),hdr=" | ".join(x.strip() for x in h),file=f[-34:]))
d=pd.DataFrame(rows);d.to_csv("data/M05_rows2.csv",index=False)
print(len(d))
pd.set_option("display.width",250)
print(d[["date","trust","prop","tenant","vals"]].to_string(max_colwidth=70))
