"""Q1 step 0: extract DKS quarterly comp sentences from EDGAR text already pulled by THESIS_SCRAPE P4
(THESIS_SCRAPE\\raw\\P4_edgar\\*.txt; read-only). Sentence split is decimal-safe. Prints comp / ticket / txn
sentences per filing so the hand-built table in q1_comp_bridge.py can be verified line by line.
Output: EVIDENCE_BOOK\\Q1\\out\\edgar_comp_sentences.txt
"""
import os, re, glob
SRC = r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\P4_edgar"
OUT = r"C:\Users\palaz\Downloads\DKS_RESEARCH\EVIDENCE_BOOK\Q1\out"
os.makedirs(OUT, exist_ok=True)
KEY = re.compile(r"(same store sales|sales per transaction|in transactions|average ticket)", re.I)
NUM = re.compile(r"\d+\.\d\s?%")
lines = []
for f in sorted(glob.glob(os.path.join(SRC, "*.txt"))):
    t = open(f, encoding="utf-8", errors="ignore").read()
    t = t.replace("\u00c2", "").replace("\u00e2\u20ac\u2122", "'").replace("\u2019", "'")
    t = re.sub(r"\s+", " ", t)
    sents = re.split(r"(?<=[a-z0-9%)])\.\s+(?=[A-Z\u2022])", t)
    seen = set()
    lines.append("== " + os.path.basename(f))
    for s in sents:
        if KEY.search(s) and NUM.search(s) and len(s) < 900:
            k = s[:150]
            if k in seen:
                continue
            seen.add(k)
            lines.append("  - " + s.strip())
open(os.path.join(OUT, "edgar_comp_sentences.txt"), "w", encoding="utf-8").write("\n".join(lines))
print(len(lines), "lines written")
