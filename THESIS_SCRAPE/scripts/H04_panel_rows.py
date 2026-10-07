"""H04: pull compact DICK'S rows (Dick... followed by $ figures) + the nearest table header years from merged snippets,
to hand-build a legacy-store sales panel.
Rerun: python H04_panel_rows.py raw/H04_dkssales_ALL_snips.txt > raw/H04_panel_rows.txt
"""
import re
import sys

t = open(sys.argv[1], encoding="utf-8").read()
seen = set()
for blk in t.split("\n#### ")[1:]:
    head, _, body = blk.partition("\n")
    url = head.split(" | ")[-1]
    for m in re.finditer(r"(Dick'?’?s?(?: Sporting Goods| House of Sport)?)\s*(\(\d\)\s*)?([^$]{0,60}?)((?:\$\s?[\d,\.]+\s*(?:[\d\.]+\s?%\s*)?){2,9})", body):
        row = re.sub(r"\s+", " ", m.group(0))[:260]
        hdr = body[max(0, m.start() - 420):m.start()]
        yrs = re.findall(r"\b(?:20[12]\d|TTM[^ ]*|\d{1,2}/\d{1,2}/20\d\d)\b", hdr)
        k = re.sub(r"\W", "", row)
        if k in seen:
            continue
        seen.add(k)
        print(f"{head[:10]} | {url.split('/')[-1]} | hdr-years:{' '.join(yrs[-9:])}\n    {row}")
