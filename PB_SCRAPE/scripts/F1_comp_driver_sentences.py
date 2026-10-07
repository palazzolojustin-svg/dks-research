"""F1: extract DKS 10-Q/10-K MD&A comp-driver sentences (categories growing/declining) into a CSV.

Rerun: python PB_SCRAPE\\scripts\\F1_comp_driver_sentences.py
Reads SOURCE\\01_DKS_SEC_FILINGS\\10-Q and \\10-K markdown files (read only) and writes
PB_SCRAPE\\raw\\F1_comp_driver_sentences.csv with filing, sentence, growth list, decline list.
For future filings, drop the new 10-Q markdown into the same folder and rerun.
"""
import csv, glob, os, re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = os.path.join(ROOT, "SOURCE", "01_DKS_SEC_FILINGS")
OUT = os.path.join(ROOT, "PB_SCRAPE", "raw", "F1_comp_driver_sentences.csv")

files = sorted(glob.glob(os.path.join(SRC, "10-Q", "*.md")) + glob.glob(os.path.join(SRC, "10-K", "*.md")))
rows = []
for f in files:
    txt = open(f, encoding="utf-8", errors="ignore").read()
    # split into sentences cheaply
    for s in re.split(r"(?<=\.)\s+", txt):
        if "comparable" in s and ("reflects" in s or "driven" in s) and ("growth in" in s or "increase" in s or "decline" in s):
            if len(s) > 900:
                continue
            g = re.search(r"growth in ([^.;]*?)(, partially offset|\.|$)", s)
            d = re.search(r"declines? in ([^.;]*?)(\.|$)", s)
            rows.append([os.path.basename(f), s.strip().replace("\n", " "), g.group(1) if g else "", d.group(1) if d else ""])
seen = set()
with open(OUT, "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["file", "sentence", "growth_categories", "decline_categories"])
    for r in rows:
        k = (r[0], r[1])
        if k in seen:
            continue
        seen.add(k)
        w.writerow(r)
print(len(seen), "rows ->", OUT)
