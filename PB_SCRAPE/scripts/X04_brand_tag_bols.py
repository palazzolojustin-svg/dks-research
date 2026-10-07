"""X04 brand tagging of DKS-bound bill-of-lading descriptions (ImportYeti free pages + Sep-2025 Wayback snapshot)."""
import json,re,csv
from collections import Counter,defaultdict
R=r"C:\Users\palaz\Downloads\DKS_RESEARCH\PB_SCRAPE\raw"
bols={}
d=json.load(open(R+r"\X04_dmsc_supplier_pages_2026-10-07.json",encoding="utf-8"))
for u,v in d.items():
    for b in v.get("recent_bols",[]):
        if re.search(r"(?i)dick",b["consignee"]): bols[b["bol"]]=(b["date"],v["name"],b["desc"])
t=open(R+r"\X04_iy_company_dick-s-merchandising-and-supply-cha.txt",encoding="utf-8").read()
for dt,b,who,desc in re.findall(r'"date":"(\d{4}-\d\d-\d\d)T[^{}]*?"bol":"([^"]*)".{0,600}?"title":"([^"]*)".{0,800}?"description":"([^"]*)"',t):
    bols.setdefault(b,(dt,who,desc))
o=open(R+r"\X04_wayback_dmsc_20250906_rsc.txt",encoding="utf-8").read()
old={}
for m in re.finditer(r'"Bill_of_Lading":"([^"]*)".{0,200}?"Product_Description":"([^"]*)","date_formatted":"(\d\d)/(\d\d)/(\d{4})","Shipper_Name":"([^"]*)"',o):
    old[m.group(1)]=(f"{m.group(5)}-{m.group(4)}-{m.group(3)}",m.group(6),m.group(2))
TAGS={"DSG":r"\bdsg\b|dicks? logo|\bdcsg\b","CALIA":r"calia|truelight|effortless","VRST":r"\bvrst\b|limitless","MAXFLI":r"maxfli|softfli|straightfli|strtfl|softfl","TOP-FLITE":r"topfli|top fli|tfxl","ETHOS":r"\bethos\b","NISHIKI":r"nishiki","QUEST":r"\bquest\b","WALTER HAGEN":r"walter hagen|\bwh\b","ALPINE DESIGN":r"alpine","FITNESS GEAR":r"fitness gear","TOMMY ARMOUR":r"tommy armour|\bta\b"}
def tag(desc): return [k for k,p in TAGS.items() if re.search(p,desc,re.I)]
for lab,B in [("2026 sample",bols),("Jul-2025 snapshot sample",old)]:
    c=Counter(); months=Counter()
    for b,(dt,who,desc) in B.items():
        months[dt[:7]]+=1
        for k in tag(desc): c[k]+=1
    print(lab,"n=",len(B),"months",sorted(months.items())[-8:])
    print("  brand-tagged BOLs:",c.most_common())
with open(R+r"\X04_dks_bols_tagged.csv","w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["sample","date","bol","shipper","tags","description"])
    for lab,B in [("2026",bols),("2025snap",old)]:
        for b,(dt,who,desc) in sorted(B.items(),key=lambda x:x[1][0]): w.writerow([lab,dt,b,who,"|".join(tag(desc)),desc])
