import sys,pandas as pd
s=sys.argv[1];parts=[]
try:
  for ch in pd.read_csv(f"raw/J02/qwi_{s}.csv.gz",dtype=str,chunksize=500000,usecols=["geography","industry","sex","agegrp","ownercode","race","ethnicity","education","firmage","firmsize","year","quarter","Emp","EmpEnd","HirA","Sep","FrmJbC","EarnBeg"]):
    parts.append(ch[(ch.industry=="4591")&(ch.sex=="0")&(ch.agegrp=="A00")&(ch.race=="A0")&(ch.ethnicity=="A0")&(ch.education=="E0")&(ch.firmage=="0")&(ch.firmsize=="0")])
  pd.concat(parts).to_csv(f"data/J02_qwi_{s}_4591.csv",index=False);print(s,"ok")
except Exception as e: print(s,"ERR",e)
