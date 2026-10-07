"""P1 helper: keyword-in-context over text files. Rerun: python P1_kwic.py "<regex>" <file_glob> [width=300] [max=40]"""
import sys, re, glob
pat = re.compile(sys.argv[1], re.I)
w = int(sys.argv[3]) if len(sys.argv) > 3 else 300
mx = int(sys.argv[4]) if len(sys.argv) > 4 else 40
for fn in sorted(glob.glob(sys.argv[2])):
    t = open(fn, encoding='utf-8', errors='ignore').read()
    n = 0; last = -10**9
    for m in pat.finditer(t):
        if m.start() - last < w:  # skip overlapping windows
            continue
        last = m.start()
        print(f'[{fn.split(chr(92))[-1][:45]}] ...{t[max(0, m.start()-w):m.end()+w]}...\n')
        n += 1
        if n >= mx:
            break
