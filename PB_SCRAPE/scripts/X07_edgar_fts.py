"""X07: SEC EDGAR full-text search for golf owned-brand mentions in OTHER companies' filings (supplier/competitor read-through).

Rerun: python X07_edgar_fts.py "\"Maxfli\"" 2024-01-01 2026-10-07
Uses the public endpoint https://efts.sec.gov/LATEST/search-index (no key; SEC asks for a descriptive User-Agent).
Prints filing date, form, filer and accession/file id for each hit. Output also saved to PB_SCRAPE\\raw\\X07_edgar_fts_<slug>.json
"""
import json
import os
import re
import sys

import requests

H = {"User-Agent": "DKS equity research (personal) research@example.com"}
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "raw")

q = sys.argv[1]
start = sys.argv[2] if len(sys.argv) > 2 else "2024-01-01"
end = sys.argv[3] if len(sys.argv) > 3 else "2026-10-07"
out = []
for frm in range(0, 500, 100):
    r = requests.get("https://efts.sec.gov/LATEST/search-index",
                     params={"q": q, "dateRange": "custom", "startdt": start, "enddt": end, "from": frm}, headers=H, timeout=60)
    if r.status_code != 200:
        print("STATUS", r.status_code, r.text[:200])
        break
    j = r.json()
    hits = j["hits"]["hits"]
    if frm == 0:
        print("total", j["hits"]["total"])
    for x in hits:
        s = x["_source"]
        out.append({"date": s.get("file_date"), "form": s.get("form"), "names": s.get("display_names"), "id": x["_id"]})
    if len(hits) < 100:
        break
for o in out:
    print(o["date"], o["form"], o["names"], o["id"])
slug = re.sub(r"[^A-Za-z0-9]+", "_", q)[:40]
with open(os.path.join(RAW, f"X07_edgar_fts_{slug}.json"), "w") as f:
    json.dump(out, f, indent=1)
