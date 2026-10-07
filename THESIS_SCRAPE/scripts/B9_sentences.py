"""B9: condense raw/B9_hos_windows.txt into unique sentences/table-fragments mentioning HoS/Field House with $ numbers.
Rerun: python B9_sentences.py  -> raw/B9_hos_sentences.txt
"""
import re
RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw"
txt = open(RAW + r"\B9_hos_windows.txt", encoding="utf-8").read()
blocks = txt.split("\n#### ")
PAT = re.compile(r"House of Sport|DHOS|Field House", re.I)
seen = set()
out = []
for b in blocks:
    if not b.strip():
        continue
    src = b.split("\n", 1)[0]
    body = b.split("\n", 1)[1] if "\n" in b else ""
    # split into pseudo-sentences
    for s in re.split(r"(?<=[a-z0-9\)])\.\s+(?=[A-Z(])", body):
        if PAT.search(s) and re.search(r"\$\s?\d|\d{2,3},\d{3}", s):
            k = re.sub(r"\W", "", s.lower())[:220]
            if k in seen:
                continue
            seen.add(k)
            out.append(f"[{src}] {s.strip()[:900]}")
open(RAW + r"\B9_hos_sentences.txt", "w", encoding="utf-8").write("\n\n".join(out))
print(len(out))
