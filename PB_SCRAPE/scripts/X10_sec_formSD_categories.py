import requests, re
from bs4 import BeautifulSoup
H={"User-Agent":"DKSResearchScript admin@example.com","Accept-Encoding":"gzip, deflate"}
j=requests.get("https://data.sec.gov/submissions/CIK0001089063.json",headers=H,timeout=30).json()
rows=[]
def scan(rec):
    for f,d,a,p in zip(rec["form"],rec["filingDate"],rec["accessionNumber"],rec["primaryDocument"]):
        if f=="SD": rows.append((d,a,p))
scan(j["filings"]["recent"])
for fx in j["filings"].get("files",[]):
    scan(requests.get("https://data.sec.gov/submissions/"+fx["name"],headers=H,timeout=30).json())
for d,a,p in sorted(rows):
    u=f"https://www.sec.gov/Archives/edgar/data/1089063/{a.replace('-','')}/{p}"
    t=re.sub(r"\s+"," ",BeautifulSoup(requests.get(u,headers=H,timeout=60).text,"html.parser").get_text(" "))
    m=re.search(r"identified Covered Products within the following categories:(.*?)(The Company has adopted|The Company's Conflict)",t)
    v=re.search(r"approximately ([\d,]+) third-party vendors",t)
    print(d, "| vendors:", v.group(1) if v else None, "|", (m.group(1).strip()[:600] if m else "n/a"), "|", u)
