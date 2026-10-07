"""WA5: Academy Sports (ASO, CIK 1817358) labor/SG&A series from EDGAR.

Pulls every ASO 10-K and 10-Q (2020-2026) from EDGAR, extracts:
  - "approximately X team members" (headcount), FT/PT split (10-K)
  - store count at period end
  - SG&A narrative sentences (strategic investments, base cost, payroll, labor, wage)
  - any sentences mentioning labor/payroll/wage/self-checkout/staffing/scheduling
Saves raw\WA5_aso_filings.json and raw\WA5_aso_headcount.csv.
Rerun: python THESIS_SCRAPE\scripts\WA5_aso_filings.py
"""
import json, re, time, csv, os, sys
import requests
from bs4 import BeautifulSoup

UA = {"User-Agent": "DKS research palazzolojustin@gmail.com"}
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, "raw")
CIK = "0001817358"

def get(url):
    for i in range(4):
        r = requests.get(url, headers=UA, timeout=60)
        if r.status_code == 200:
            return r
        time.sleep(1.5 * (i + 1))
    r.raise_for_status()

sub = get(f"https://data.sec.gov/submissions/CIK{CIK}.json").json()
rec = sub["filings"]["recent"]
rows = []
for form, acc, doc, fdate, rdate in zip(rec["form"], rec["accessionNumber"], rec["primaryDocument"], rec["filingDate"], rec["reportDate"]):
    if form in ("10-K", "10-Q"):
        rows.append(dict(form=form, acc=acc, doc=doc, filed=fdate, period=rdate))
rows.sort(key=lambda x: x["period"])

KEY = re.compile(r"(labor|payroll|wage|self-checkout|self checkout|staffing|scheduling|team member|store employee|hourly|minimum wage|base cost|expense discipline|cost savings|productivity|efficienc)", re.I)
out = []
for r in rows:
    url = f"https://www.sec.gov/Archives/edgar/data/1817358/{r['acc'].replace('-','')}/{r['doc']}"
    try:
        html = get(url).text
    except Exception as e:
        print("fail", url, e); continue
    text = BeautifulSoup(html, "html.parser").get_text(" ")
    text = re.sub(r"\s+", " ", text)
    tm = re.findall(r"approximately ([\d,]+) team members", text, re.I)
    ftpt = re.findall(r"([\d]+)% (?:were )?full[- ]time[^.]{0,80}?([\d]+)% (?:were )?part[- ]time", text, re.I)
    stores = re.findall(r"(?:operated|we had|consisted of|operate) ([\d,]+) (?:stores|retail locations|\"Academy Sports \+ Outdoors\" retail locations)", text, re.I)
    sents = re.split(r"(?<=[.;])\s+", text)
    sga = [s for s in sents if re.search(r"selling, general and administrative expenses (increased|decreased)", s, re.I)]
    kw = [s for s in sents if KEY.search(s) and len(s) < 700]
    r2 = dict(r, url=url, team_members=tm, ftpt=ftpt, stores=stores[:5], sga_sentences=sga[:6], keyword_sentences=kw)
    out.append(r2)
    print(r["form"], r["period"], tm[:2], stores[:2], ftpt[:1])
    time.sleep(0.4)

json.dump(out, open(os.path.join(RAW, "WA5_aso_filings.json"), "w", encoding="utf-8"), indent=1)
with open(os.path.join(RAW, "WA5_aso_headcount.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["form", "period", "filed", "team_members", "stores_mentions", "ftpt", "url"])
    for r in out:
        w.writerow([r["form"], r["period"], r["filed"], ";".join(r["team_members"]), ";".join(r["stores"]), str(r["ftpt"]), r["url"]])
print("done", len(out))
