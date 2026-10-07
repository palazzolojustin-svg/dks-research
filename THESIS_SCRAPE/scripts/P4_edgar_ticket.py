"""P4: pull DKS 10-Q / 10-K primary documents (FY2012-FY2022) from SEC EDGAR and extract the MD&A
comparable-sales decomposition sentences (sales per transaction / transactions / ticket).
(Earnings press releases pre-2023 do NOT state the split; the 10-Q/10-K MD&A does.)
Rerun: python P4_edgar_ticket.py   -> THESIS_SCRAPE/raw/P4_edgar/<date>_<form>.txt and raw/P4_edgar_ticket_sentences.csv
"""
import requests, re, time, csv, os, html, sys
from bs4 import BeautifulSoup

UA = {"User-Agent": "DKS research palazzolojustin@gmail.com", "Accept-Encoding": "gzip, deflate"}
BASE = r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw"
OUT = os.path.join(BASE, "P4_edgar")
os.makedirs(OUT, exist_ok=True)
CIK = "0001089063"
START, END = sys.argv[1] if len(sys.argv) > 1 else "2012-05-01", sys.argv[2] if len(sys.argv) > 2 else "2023-01-01"

def get(url):
    for i in range(3):
        try:
            r = requests.get(url, headers=UA, timeout=30)
            if r.status_code == 200:
                return r
        except Exception as e:
            print("err", e, flush=True)
        time.sleep(2 + i)
    raise RuntimeError(url)

sub = get(f"https://data.sec.gov/submissions/CIK{CIK}.json").json()
rows = []
def add(b):
    rows.extend(zip(b["form"], b["filingDate"], b["accessionNumber"], b["primaryDocument"], b["reportDate"]))
add(sub["filings"]["recent"])
for extra in sub["filings"].get("files", []):
    add(get("https://data.sec.gov/submissions/" + extra["name"]).json())
targets = sorted([r for r in rows if r[0] in ("10-Q", "10-K") and START <= r[1] <= END], key=lambda x: x[1])
print(len(targets), "filings", flush=True)
pat = re.compile(r"[^.]{0,300}\b(sales per transaction|transactions|ticket)\b[^.]{0,300}\.", re.I)
out_rows = []
for form, d, acc, prim, rep in targets:
    fn = os.path.join(OUT, f"{d}_{form}_{rep}.txt")
    if os.path.exists(fn):
        txt = open(fn, encoding="utf-8").read()
    else:
        url = f"https://www.sec.gov/Archives/edgar/data/1089063/{acc.replace('-', '')}/{prim}"
        t = get(url).text
        txt = re.sub(r"\s+", " ", html.unescape(BeautifulSoup(t, "lxml").get_text(" ")))
        open(fn, "w", encoding="utf-8").write(txt)
        time.sleep(0.4)
    n = 0
    for m in pat.finditer(txt):
        s = m.group(0).strip()
        if re.search(r"comparable|same store|consolidated same", s, re.I):
            out_rows.append([d, form, rep, s]); n += 1
    print(d, form, rep, n, flush=True)

with open(os.path.join(BASE, "P4_edgar_ticket_sentences.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh); w.writerow(["filing_date", "form", "period", "sentence"]); w.writerows(out_rows)
print(len(out_rows), "sentences", flush=True)
