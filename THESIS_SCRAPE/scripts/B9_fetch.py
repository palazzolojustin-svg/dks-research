"""B9: fetch EDGAR docs listed in raw/B9_fts_<TAG>.csv that are not already cached (H04_edgar_cache) into raw/B9_edgar_cache.

Rerun: python B9_fetch.py TAG [form_regex]
"""
import csv
import html
import os
import re
import sys
import time
import requests

RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw"
C1 = os.path.join(RAW, "H04_edgar_cache")
C2 = os.path.join(RAW, "B9_edgar_cache")
os.makedirs(C2, exist_ok=True)
H = {"User-Agent": "IndependentResearch research-script contact@example.org"}
tag = sys.argv[1]
freg = re.compile(sys.argv[2] if len(sys.argv) > 2 else r"FWP|424|8-K|10-K|10-Q")


def cname(u):
    return re.sub(r"[^A-Za-z0-9_.-]", "_", u.split("/data/")[1]) + ".txt"


rows = list(csv.DictReader(open(os.path.join(RAW, f"B9_fts_{tag}.csv"), encoding="utf-8")))
for r in rows:
    if not freg.search(r["form"]):
        continue
    u = r["url"]
    n = cname(u)
    if os.path.exists(os.path.join(C1, n)) or os.path.exists(os.path.join(C2, n)):
        continue
    time.sleep(0.3)
    try:
        resp = requests.get(u, headers=H, timeout=240)
    except Exception as e:
        print("ERR", u, type(e).__name__, flush=True)
        continue
    raw = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", resp.text)
    raw = re.sub(r"(?s)<[^>]+>", " ", raw)
    txt = re.sub(r"\s+", " ", html.unescape(raw))
    open(os.path.join(C2, n), "w", encoding="utf-8").write(txt)
    print("got", r["file_date"], r["form"], len(txt), u, flush=True)
