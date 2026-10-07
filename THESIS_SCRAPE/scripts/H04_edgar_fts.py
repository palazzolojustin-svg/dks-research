"""H04: EDGAR full-text search for a phrase, then fetch every non-DKS/FL hit and extract context.

Rerun: python H04_edgar_fts.py "\"House of Sport\"" HoS [startdt] [enddt]
Outputs:
  THESIS_SCRAPE/raw/H04_edgar_<tag>_hits.csv   (all hits: date, form, filer, url)
  THESIS_SCRAPE/raw/H04_edgar_<tag>_context.txt (keyword context per non-DKS document)
  doc cache: THESIS_SCRAPE/raw/H04_edgar_cache/
"""
import csv
import os
import re
import sys
import time
import requests
from bs4 import BeautifulSoup

RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw"
CACHE = os.path.join(RAW, "H04_edgar_cache")
os.makedirs(CACHE, exist_ok=True)
H = {"User-Agent": "IndependentResearch research-script contact@example.org"}
q, tag = sys.argv[1], sys.argv[2]
q = q.replace("'", '"')  # PowerShell strips double quotes: pass 'House of Sport' wrapped in single quotes inside
if not q.startswith('"'):
    q = '"' + q + '"'
start = sys.argv[3] if len(sys.argv) > 3 else "2023-01-01"
end = sys.argv[4] if len(sys.argv) > 4 else "2026-10-07"
SKIP = re.compile(r"DICK'S SPORTING|FOOT LOCKER", re.I)
CTX_RX = re.compile(r"House of Sport|Field House|Dick'?s|DICK", re.I)

hits = []
frm = 0
while True:
    r = requests.get("https://efts.sec.gov/LATEST/search-index",
                     params={"q": q, "dateRange": "custom", "startdt": start, "enddt": end, "from": frm},
                     headers=H, timeout=60)
    d = r.json()
    if "hits" not in d:
        print("FTS error", r.status_code, str(d)[:300], "from", frm)
        break
    hh = d["hits"]["hits"]
    if not hh:
        break
    for x in hh:
        s = x["_source"]
        adsh, fn = x["_id"].split(":", 1)
        cik = s["ciks"][0].lstrip("0")
        url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{adsh.replace('-', '')}/{fn}"
        hits.append([s.get("file_date"), s.get("form"), "; ".join(s.get("display_names", [])), url])
    frm += len(hh)
    if frm >= d["hits"]["total"]["value"]:
        break
    time.sleep(0.5)

hits.sort()
with open(os.path.join(RAW, f"H04_edgar_{tag}_hits.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["file_date", "form", "filer", "url"])
    w.writerows(hits)
print("hits", len(hits))

out = open(os.path.join(RAW, f"H04_edgar_{tag}_context.txt"), "w", encoding="utf-8")
for fd, form, filer, url in hits:
    if SKIP.search(filer) or url.lower().endswith(".pdf"):
        continue
    cp = os.path.join(CACHE, re.sub(r"[^A-Za-z0-9_.-]", "_", url.split("/data/")[1]) + ".txt")
    if os.path.exists(cp):
        txt = open(cp, encoding="utf-8").read()
    else:
        time.sleep(0.3)
        try:
            rr = requests.get(url, headers=H, timeout=120)
        except Exception as e:
            print("ERR", url, e)
            continue
        soup = BeautifulSoup(rr.text, "lxml") if len(rr.text) < 3e7 else None
        txt = soup.get_text(" ") if soup else rr.text
        txt = re.sub(r"\s+", " ", txt)
        open(cp, "w", encoding="utf-8").write(txt)
    out.write(f"\n########## {fd} | {form} | {filer} | {url}\n")
    for m in re.finditer(r"House of Sport", txt, re.I):
        a, b = max(0, m.start() - 700), min(len(txt), m.end() + 700)
        out.write("... " + txt[a:b] + " ...\n")
    print(fd, form, filer[:60], "len", len(txt), flush=True)
out.close()
