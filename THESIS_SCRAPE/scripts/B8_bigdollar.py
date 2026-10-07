"""B8 wave3: find DICK'S/Golf Galaxy/HoS rows followed (<=260 chars) by a dollar figure between $4M and $60M (= store sales, not rent),
or by an explicit sales-PSF/occupancy-cost pair. Output raw/B8_bigdollar.txt (one line per unique hit, with property + filing).
Rerun: python B8_bigdollar.py
"""
import os, re, glob
RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw"
files = glob.glob(os.path.join(RAW, "H04_edgar_cache", "*.txt")) + glob.glob(os.path.join(RAW, "B8_cache", "*.txt"))
NAME = re.compile(r"(?:Dick[’'`]s|Dicks\b|DICK[’']S|Golf Galaxy|House of Sport|Field House)")
DOL = re.compile(r"\$\s?(\d{1,2}(?:,\d{3}){2})\b|\$\s?(\d{1,2}\.\d{1,2}) ?(?:million|mn|MM)")
PROP = re.compile(r"No\.\s?\d{1,2}\s?[–-]\s?([A-Z][^.$]{2,60}?)\s+(?:The following|Mortgage Loan Information|Mortgaged Property Information|Market Overview|Historical|Cash Flow|Underwritten|Major Tenants|Tenant Summary|Sales|Anchor)")
BAD = re.compile(r"billion|Balance|appraised|Sale Price|Dickinson|reserve|Reserve|TI/LC|loan|Loan Amount|Cut-off|Purchase", re.I)
seen = set(); out = []
for fp in sorted(files):
    t = open(fp, encoding="utf-8", errors="ignore").read()
    k = os.path.basename(fp)
    for m in NAME.finditer(t):
        w = t[m.start(): m.start() + 260]
        if BAD.search(w[:120]): continue
        hit = None
        for d in DOL.finditer(w):
            v = float(d.group(1).replace(",", "")) if d.group(1) else float(d.group(2)) * 1e6
            if 4e6 <= v <= 6e7:
                hit = v; break
        if not hit: continue
        s = re.sub(r"\s+", " ", w)
        back = t[max(0, m.start() - 80000): m.start()]
        pm = list(PROP.finditer(back)); prop = pm[-1].group(1).strip() if pm else "?"
        key = (prop[:20], round(hit))
        if key in seen: continue
        seen.add(key)
        out.append(f"{prop} | {k[:70]} | {hit:,.0f} | {s}")
open(os.path.join(RAW, "B8_bigdollar.txt"), "w", encoding="utf-8").write("\n".join(sorted(out)))
print(len(out))
