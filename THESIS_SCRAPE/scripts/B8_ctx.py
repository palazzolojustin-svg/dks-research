"""B8 helper: print context around a keyword in cached CMBS docs. python B8_ctx.py <docsubstring> <keyword> [before] [after] [maxhits]"""
import sys, glob, os
RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw"
sub, kw = sys.argv[1], sys.argv[2]
b = int(sys.argv[3]) if len(sys.argv) > 3 else 1500
a = int(sys.argv[4]) if len(sys.argv) > 4 else 1500
mx = int(sys.argv[5]) if len(sys.argv) > 5 else 3
fs = [f for d in ["H04_edgar_cache", "B8_cache"] for f in glob.glob(os.path.join(RAW, d, "*" + sub + "*"))]
for f in fs[:1]:
    t = open(f, encoding="utf-8", errors="ignore").read()
    i, n = 0, 0
    while n < mx:
        i = t.find(kw, i)
        if i < 0: break
        print("=====", os.path.basename(f), i); print(t[max(0, i - b): i + a]); i += len(kw); n += 1
