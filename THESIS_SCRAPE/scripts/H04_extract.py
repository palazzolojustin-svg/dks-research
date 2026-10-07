"""H04: extract keyword sentences (with speaker + date) from saved transcript text files.

Rerun: python H04_extract.py <glob under THESIS_SCRAPE/raw, e.g. H04_MAC_20*.txt> [regex] [context_sentences]
"""
import glob
import os
import re
import sys

RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw"
pat = re.compile(sys.argv[2] if len(sys.argv) > 2 else r"Dick|House of Sport|Field House", re.I)
ctx = int(sys.argv[3]) if len(sys.argv) > 3 else 2

for fp in sorted(glob.glob(os.path.join(RAW, sys.argv[1]))):
    lines = open(fp, encoding="utf-8").read().split("\n")
    date = next((l for l in lines[:40] if re.search(r"(20\d\d)", l) and re.search(r"Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec", l)), "")
    print("#" * 10, os.path.basename(fp), "|", date.strip())
    speaker = "?"
    for i, ln in enumerate(lines):
        s = ln.strip()
        if 0 < len(s) < 40 and i + 1 < len(lines) and lines[i + 1].strip() == ":":
            speaker = s
            continue
        if len(s) < 60:
            continue
        sents = re.split(r"(?<=[.!?])\s+", s)
        hit = [k for k, x in enumerate(sents) if pat.search(x)]
        if not hit:
            continue
        keep = set()
        for k in hit:
            keep.update(range(max(0, k - ctx), min(len(sents), k + ctx + 1)))
        print(f"  [{speaker}] " + " ".join(sents[k] for k in sorted(keep)))
