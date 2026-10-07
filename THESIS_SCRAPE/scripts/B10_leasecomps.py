"""B10 side-pass: DICK'S lease comparables (appraiser 'Retail Rent Comparables' tables) in all cached CMBS docs.
Rerun: python B10_leasecomps.py -> raw/B10_dks_lease_comps.txt (unique snippets: DICK'S + SF + date + rent)
"""
import os, re, glob
RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw"
fs = [f for d in ["B10_cache", "B8_cache", "H04_edgar_cache"] for f in glob.glob(os.path.join(RAW, d, "*_000*.txt"))]
M = re.compile(r"(Dick[’'`]?s(?: Sporting Goods)?|DICK[’']S(?: Sporting Goods)?)\s+(?:\(\d\)\s+)?(?:[A-Z][\w’'&.]+\s+){0,3}?([\d,]{5,7})\s+(?:[\d,]{4,7}\s+)?((?:[A-Z][a-z]{2}\.?|\d{1,2}/\d{1,2}/)\s?\d{2,4}|\d{4}|[A-Z][a-z]+ \d{4})")
out, seen = [], set()
for f in fs:
    t = open(f, encoding="utf-8", errors="ignore").read()
    if "Comparable" not in t and "comparable" not in t: continue
    for m in M.finditer(t):
        s = t[m.start(): m.start() + 200]
        if not re.search(r"NNN|Net|Gross|\$\d", s[:160]): continue
        if re.search(r"Baa|BBB|NR/|NR /|% of", s[:80]): continue
        k = re.sub(r"\W", "", s[:90])
        if k in seen: continue
        seen.add(k)
        out.append((os.path.basename(f), t[max(0, m.start() - 180): m.start()], s))
with open(os.path.join(RAW, "B10_dks_lease_comps.txt"), "w", encoding="utf-8") as o:
    for fn, b, s in out:
        o.write(f"## {fn}\n   BEFORE: {b}\n   ROW: {s}\n")
print(len(out))
