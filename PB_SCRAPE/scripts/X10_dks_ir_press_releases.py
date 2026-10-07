"""X10_dks_ir_press_releases.py
Pulls every DICK'S Sporting Goods press release (headline, date, body text) from the public Q4 IR JSON feed
used by investors.dicks.com, for the years given, and flags those mentioning owned/vertical brands.
Rerun: python X10_dks_ir_press_releases.py 2024 2025 2026
Output: PB_SCRAPE/raw/X10_dks_press_releases.json and X10_dks_press_releases_ownedbrand_hits.csv
"""
import requests, json, sys, re, csv, html, os
H={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36","Accept":"application/json"}
BASE="https://investors.dicks.com/feed/PressRelease.svc/GetPressReleaseList?LanguageId=1&bodyType=1&pressReleaseDateFilter=3&pageSize=-1&pageNumber=0&year={y}"
BRANDS=["vertical brand","CALIA","VRST","DSG","MAXFLI","Maxfli","Walter Hagen","Top-Flite","Top Flite","Tommy Armour","Alpine Design","ETHOS","Fitness Gear","Nishiki","Quest","owned brand","private label","exclusive brand"]
out=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","raw")
years=sys.argv[1:] or ["2024","2025","2026"]
allrows=[]
for y in years:
    r=requests.get(BASE.format(y=y),headers=H,timeout=60); r.raise_for_status()
    for it in r.json()["GetPressReleaseListResult"]:
        body=re.sub(r"<[^>]+>"," ",html.unescape(it.get("Body") or "")); body=re.sub(r"\s+"," ",body)
        hits={b:len(re.findall(r"\b"+re.escape(b)+r"\b",body+" "+it["Headline"])) for b in BRANDS}
        hits={k:v for k,v in hits.items() if v}
        allrows.append({"date":it.get("PressReleaseDate"),"headline":it["Headline"],"url":"https://investors.dicks.com"+(it.get("LinkToDetailPage") or ""),"pdf":it.get("DocumentPath"),"hits":hits,"body":body})
json.dump(allrows,open(os.path.join(out,"X10_dks_press_releases.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
with open(os.path.join(out,"X10_dks_press_releases_ownedbrand_hits.csv"),"w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["date","headline","hits","url"])
    for a in allrows:
        if a["hits"]: w.writerow([a["date"],a["headline"],json.dumps(a["hits"]),a["url"]])
print(len(allrows),"releases")
for a in allrows: print(a["date"][:10] if a["date"] else "", "|", a["headline"][:110], "|", a["hits"])

