"""H04: dedupe DICK'S sales/occupancy sentences from snippet files.
Rerun: python H04_sales_sentences.py raw/H04_dkssales_<TAG>_snips.txt
"""
import re
import sys

t = open(sys.argv[1], encoding="utf-8").read()
seen = {}
for blk in t.split("\n#### ")[1:]:
    head, _, body = blk.partition("\n")
    url = head.split(" | ")[-1]
    for s in re.split(r"(?<=[.;])\s+(?=[A-Z(])", body):
        if re.search(r"Dick", s, re.I) and re.search(r"\$\s?\d", s) and re.search(r"sales|occupancy cost|PSF|rent", s, re.I):
            k = re.sub(r"\W", "", s)[:160]
            if k not in seen:
                seen[k] = (head[:10], url, s.strip())
for d, u, s in sorted(seen.values()):
    print(f"[{d}] {u}\n   {s[:900]}\n")
