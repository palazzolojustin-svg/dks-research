"""B9: scan cached EDGAR docs (H04_edgar_cache + B9_edgar_cache) for House of Sport / Field House windows.

Rerun: python B9_cache_scan.py
Writes raw/B9_hos_windows.txt (deduped windows around HoS/DHOS/Field House mentions that carry $ or SF numbers)
"""
import os
import re
import glob

RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw"
files = glob.glob(os.path.join(RAW, "H04_edgar_cache", "*.txt")) + glob.glob(os.path.join(RAW, "B9_edgar_cache", "*.txt")) + glob.glob(os.path.join(RAW, "B8_cache", "*.txt"))
PAT = re.compile(r"House of Sport|DHOS|Field House|DICK'?S Field|Dick.?s Field", re.I)
NUM = re.compile(r"\$\s?\d|\d{2,3},\d{3}\s*(SF|square)", re.I)
seen = set()
out = open(os.path.join(RAW, "B9_hos_windows.txt"), "w", encoding="utf-8")
cnt = {}
for fp in sorted(files):
    txt = open(fp, encoding="utf-8", errors="ignore").read()
    n = 0
    for m in PAT.finditer(txt):
        a, b = max(0, m.start() - 500), min(len(txt), m.end() + 700)
        w = txt[a:b]
        if not NUM.search(w):
            continue
        key = re.sub(r"\W", "", txt[max(0, m.start() - 120):m.start() + 200])
        if key in seen:
            continue
        seen.add(key)
        n += 1
        out.write(f"\n#### {os.path.basename(fp)}\n... {w} ...\n")
    if n:
        cnt[os.path.basename(fp)] = n
out.close()
for k, v in sorted(cnt.items(), key=lambda z: -z[1]):
    print(v, k)
print("files", len(files), "with hits", len(cnt))

