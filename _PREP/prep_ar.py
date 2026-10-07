"""Sentence-level delta for Annual Reports to Shareholders vs the same-year 10-K.

The annual reports are PDF extractions with different line wrapping from the EDGAR 10-K text, so a
line-level comparison fails. Here both documents are flattened, split into sentences / table cells,
normalized to lowercase alphanumerics, and every AR segment not found in the 10-K is kept with the
approximate original line number.
"""
import os, re, json

ROOT = os.path.join(os.path.expanduser(r"~\Downloads"), "DKS_RESEARCH")
SRC = os.path.join(ROOT, "SOURCE")
OUT = os.path.join(ROOT, "_PREP", "deltas")

def segs(text):
    # returns list of (line_no, raw_segment)
    out = []
    buf, start = [], None
    for i, l in enumerate(text.splitlines(), 1):
        s = l.strip()
        if not s or s.startswith("<!-- page"):
            continue
        for piece in re.split(r"(?<=[.;:!?])\s+|\s*\|\s*|\s{3,}", s):
            if not piece:
                continue
            if start is None:
                start = i
            buf.append(piece)
            if re.search(r"[.;:!?]$", piece) or len(" ".join(buf)) > 300 or "|" in l:
                out.append((start, " ".join(buf)))
                buf, start = [], None
    if buf:
        out.append((start, " ".join(buf)))
    return out

def key(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())

def read(p):
    with open(os.path.join(SRC, p), encoding="utf-8", errors="replace") as fh:
        return fh.read()

stats = []
ar = r"02_DKS_TRANSCRIPTS\annual_report_letters" + "\\"
k = r"01_DKS_SEC_FILINGS\10-K" + "\\"
for a, kk in [("2023-05-05", "FY2022_filed-2023-03-23"), ("2024-05-02", "FY2023_filed-2024-03-28"),
              ("2025-05-02", "FY2024_filed-2025-03-27"), ("2026-05-01", "FY2025_filed-2026-03-27")]:
    arp, kp = ar + f"DKS_Annual-Report-to-Shareholders_{a}.md", k + f"DKS_10-K_{kk}.md"
    kflat = key(read(kp))
    kset = {key(s) for _, s in segs(read(kp))}
    keep, total = [], 0
    for ln, s in segs(read(arp)):
        kk2 = key(s)
        if len(kk2) < 4:
            continue
        total += 1
        if kk2 in kset or (len(kk2) >= 25 and kk2 in kflat):
            continue
        keep.append(f"L{ln}: {s}")
    name = arp.replace("\\", "__").replace(".md", "") + ".delta.md"
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as fh:
        fh.write(f"# DELTA (sentence-level) of SOURCE/{arp}\n# Reference: SOURCE/{kp}\n")
        fh.write(f"# {len(keep)} of {total} text segments are NOT found in the reference 10-K (normalized text match); all others are repeats of the 10-K.\n")
        fh.write("# Short numeric fragments may appear here only because the PDF extraction split table cells differently; check context in the original around the given line.\n\n")
        fh.write("\n".join(keep) + "\n")
    stats.append({"variant": arp, "refs": [kp], "segments": total, "delta_segments": len(keep), "delta_file": "_PREP/deltas/" + name})
    print(f"{100*len(keep)/total:5.1f}%  {len(keep)}/{total}  {arp}  ({os.path.getsize(os.path.join(OUT, name))//1024} KB)")

with open(os.path.join(ROOT, "_PREP", "delta_stats_ar.json"), "w") as fh:
    json.dump(stats, fh, indent=1)
