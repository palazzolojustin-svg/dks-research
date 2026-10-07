"""B10: print context for a regex in a cached doc: nearest preceding 'Loan No.'/'Mortgaged Property' heading + footnotes after.
Usage: python B10_ctx.py <docname-substring> <regex> [after_chars] [before_chars]
"""
import os, re, sys, glob
RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw"
fs = [f for d in ["B10_cache", "B8_cache", "H04_edgar_cache"] for f in glob.glob(os.path.join(RAW, d, "*" + sys.argv[1] + "*"))]
aft = int(sys.argv[3]) if len(sys.argv) > 3 else 1500
bef = int(sys.argv[4]) if len(sys.argv) > 4 else 300
t = open(fs[0], encoding="utf-8", errors="ignore").read()
print("DOC", fs[0])
for m in list(re.finditer(sys.argv[2], t))[:4]:
    back = t[max(0, m.start() - 120000): m.start()]
    hs = list(re.finditer(r"(Collateral Asset Summary\s*[–-]\s*Loan No\.\s*\d+\s+[^$]{3,60}?\s+Cut-off|Loan No\.\s*\d+\s*[–-]\s*[A-Z][^$]{3,60}?\s{1,3}(?=[A-Z]))", back))
    print("@", m.start(), "| HEAD:", hs[-1].group(0)[:120] if hs else "?")
    print(t[max(0, m.start() - bef): m.start() + aft])
    print("-----")
