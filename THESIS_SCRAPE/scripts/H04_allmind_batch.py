"""H04: batch-download REIT earnings-call transcripts from allmind.ai public event pages.

Rerun: python H04_allmind_batch.py TICK1,TICK2 [quarters e.g. 2024_Q1..2026_Q2 default]
Saves THESIS_SCRAPE/raw/H04_<TICK>_<yyyy>_<Qn>.txt (skips existing), prints status/size.
"""
import os
import sys
import re
import time
import requests
from bs4 import BeautifulSoup

RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"}
QS = [f"{y}_Q{q}" for y in (2024, 2025, 2026) for q in (1, 2, 3, 4)]
QS = [x for x in QS if x <= "2026_Q2"]

for t in sys.argv[1].split(","):
    for q in QS:
        fp = os.path.join(RAW, f"H04_{t}_{q}.txt")
        if os.path.exists(fp) and os.path.getsize(fp) > 5000:
            continue
        url = f"https://allmind.ai/earnings/event/bt_{t}_{q}"
        r = None
        for attempt in range(3):
            time.sleep(6 + 20 * attempt)
            try:
                r = requests.get(url, headers=UA, timeout=45)
                break
            except Exception as e:
                print(t, q, "ERR", type(e).__name__, flush=True)
        if r is None:
            continue
        soup = BeautifulSoup(r.text, "html.parser")
        for x in soup(["script", "style", "noscript"]):
            x.decompose()
        txt = re.sub(r"\n\s*\n+", "\n", soup.get_text("\n"))
        n = len(re.findall(r"Dick|House of Sport", txt, re.I))
        print(t, q, r.status_code, len(txt), "DKS-hits", n, flush=True)
        if r.status_code == 200 and len(txt) > 5000:
            open(fp, "w", encoding="utf-8").write(url + "\n" + txt)
