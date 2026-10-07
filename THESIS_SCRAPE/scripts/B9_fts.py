"""B9: EDGAR full-text search listing for HoS / Field House CMBS disclosures.

Rerun: python B9_fts.py TAG "phrase1&&phrase2" ["..."]   (env B9_FORMS=FWP,424B2,424H optional; B9_START=2023-01-01)
Writes raw/B9_fts_<TAG>.csv (file_date, form, filer, url, query). Excludes DKS/FL own filings and PDFs.
"""
import csv
import os
import re
import sys
import time
import requests

RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw"
H = {"User-Agent": "IndependentResearch research-script contact@example.org"}
tag = sys.argv[1]
queries = sys.argv[2:]
forms = os.environ.get("B9_FORMS", "")
start = os.environ.get("B9_START", "2023-01-01")


def fts(qq):
    out, frm = [], 0
    while True:
        p = {"q": qq, "dateRange": "custom", "startdt": start, "enddt": "2026-10-07", "from": frm}
        if forms:
            p["forms"] = forms
        for attempt in range(4):
            try:
                r = requests.get("https://efts.sec.gov/LATEST/search-index", params=p, headers=H, timeout=60)
                d = r.json()
                break
            except Exception as e:
                time.sleep(2 + attempt * 3)
                d = {}
        if "hits" not in d:
            break
        hh = d["hits"]["hits"]
        if not hh:
            break
        out += hh
        frm += len(hh)
        if frm >= d["hits"]["total"]["value"] or frm >= 1000:
            break
        time.sleep(0.4)
    return out


rows = {}
for q in queries:
    qq = " ".join(f'"{p.strip()}"' for p in q.split("&&"))
    hh = fts(qq)
    print(q, len(hh), flush=True)
    for x in hh:
        s = x["_source"]
        adsh, fn = x["_id"].split(":", 1)
        if re.search(r"DICK'S SPORTING|FOOT LOCKER", " ".join(s.get("display_names", [])), re.I):
            continue
        if fn.lower().endswith(".pdf"):
            continue
        cik = s["ciks"][0].lstrip("0")
        url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{adsh.replace('-', '')}/{fn}"
        rows.setdefault(url, [s.get("file_date"), s.get("form"), (s.get("display_names") or [""])[0][:80], url, q])
with open(os.path.join(RAW, f"B9_fts_{tag}.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["file_date", "form", "filer", "url", "query"])
    for r in sorted(rows.values(), key=lambda z: z[0]):
        w.writerow(r)
print("unique", len(rows))
