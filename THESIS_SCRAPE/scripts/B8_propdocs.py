"""B8: for each property keyword, list cached CMBS docs that contain it and print every DICK'S sales line near a sales header in that doc.
Rerun: python B8_propdocs.py "Crossgates Mall" "Westroads Mall" ...  -> stdout
"""
import os, re, glob, sys
RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw"
files = glob.glob(os.path.join(RAW, "H04_edgar_cache", "*.txt")) + glob.glob(os.path.join(RAW, "B8_cache", "*.txt"))
props = sys.argv[1:]
NAME = re.compile(r"(?:Dick[’'`]s|Dicks\b|DICK[’']S)")
res = {p: [] for p in props}
for fp in files:
    t = open(fp, encoding="utf-8", errors="ignore").read()
    for p in props:
        idx = [m.start() for m in re.finditer(re.escape(p), t)]
        if not idx: continue
        lines = set()
        for i in idx[:400]:
            seg = t[i: i + 6000]
            for m in NAME.finditer(seg):
                w = re.sub(r"\s+", " ", seg[m.start(): m.start() + 200])
                if re.search(r"\$\s?\d[\d,]{4,}|\$\d{3}\b|sales|Sales", w) and re.search(r"(?:Sales|sales|PSF|Occ)", seg[max(0, m.start() - 1200): m.start()]):
                    lines.add(w[:200])
        res[p].append((os.path.basename(fp)[:70], sorted(lines)[:12]))
for p in props:
    print("#####", p, len(res[p]), "docs")
    for d, ls in sorted(res[p]):
        print("  ", d)
        for l in ls: print("      ", l)
