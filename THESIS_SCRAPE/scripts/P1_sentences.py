"""P1 helper: print unique SENTENCES matching a regex from files (dedup across files).
Rerun: python P1_sentences.py "<regex>" "<glob>" [maxlen=600]"""
import sys, re, glob
pat = re.compile(sys.argv[1], re.I)
mx = int(sys.argv[3]) if len(sys.argv) > 3 else 600
seen = set()
for fn in sorted(glob.glob(sys.argv[2])):
    t = open(fn, encoding='utf-8', errors='ignore').read()
    sents = re.split(r'(?<=[.;])\s+(?=[A-Z•])', t)
    out = []
    for s in sents:
        if pat.search(s):
            k = re.sub(r'\W+', '', s.lower())[:200]
            if k in seen:
                continue
            seen.add(k); out.append(s.strip()[:mx])
    if out:
        print('=====', fn.split('\\')[-1][:60])
        for s in out:
            print(' -', s)
