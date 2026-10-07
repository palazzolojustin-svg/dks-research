r"""N2_8k_vertical_language.py
Extract every clause mentioning vertical/owned brands from DKS 8-K covers and exhibits in SOURCE,
to build a dated series of how DKS press releases describe vertical brands (exec quotes + FLS risk wording).
Rerun:  python PB_SCRAPE/scripts/N2_8k_vertical_language.py   -> writes PB_SCRAPE/raw/N2_8k_vertical_language.csv
Extend: put new 8-K exhibit text (.md/.txt, from EDGAR) under ROOT; filename must contain YYYY-MM-DD.
"""
import re, csv, pathlib, sys
ROOT = pathlib.Path(r"C:\Users\palaz\Downloads\DKS_RESEARCH\SOURCE\01_DKS_SEC_FILINGS\8-K")
if len(sys.argv) > 1:
    ROOT = pathlib.Path(sys.argv[1])
OUT = pathlib.Path(r"C:\Users\palaz\Downloads\DKS_RESEARCH\PB_SCRAPE\raw\N2_8k_vertical_language.csv")
pat = re.compile(r"(?i)vertical|private (label|brand)|owned brand|exclusive brand|CALIA|VRST|Maxfli|Walter Hagen|Alpine Design")
rows = []
for f in sorted(list(ROOT.rglob("*.md")) + list(ROOT.rglob("*.txt"))):
    txt = f.read_text(encoding="utf-8", errors="ignore").replace("\n", " ")
    m = re.search(r"(\d{4}-\d{2}-\d{2})", f.name)
    d = m.group(1) if m else ""
    for mm in pat.finditer(txt):
        s = max(0, mm.start() - 260); e = min(len(txt), mm.end() + 200)
        rows.append({"date": d, "file": str(f.relative_to(ROOT)), "term": mm.group(0),
                     "context": re.sub(r"\s+", " ", txt[s:e])})
rows.sort(key=lambda r: r["date"])
with OUT.open("w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["date", "file", "term", "context"]); w.writeheader(); w.writerows(rows)
print(len(rows), "hits")
for r in rows:
    print(r["date"], r["file"][:70], "|", r["context"][:460])
    print("---")
