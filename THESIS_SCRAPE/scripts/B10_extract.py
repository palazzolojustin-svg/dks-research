"""B10: extract DICK'S / Golf Galaxy / HoS / FH sales evidence from the NEW CMBS docs in raw/B10_cache.
Rerun: python B10_extract.py -> raw/B10_review.txt (sentences + table rows with headers, per doc, for manual coding)
"""
import os, re, csv
RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw"
C3 = os.path.join(RAW, "B10_cache")
meta = {}
for hf in ["B10_fts_hits.csv", "B10_fts2_hits.csv", "B10_fts3_hits.csv"]:
    if not os.path.exists(os.path.join(RAW, hf)): continue
    for r in csv.DictReader(open(os.path.join(RAW, hf), encoding="utf-8")):
        if not re.match(r"^(FWP|424B\d|424H)", r["form"]): continue
        k = re.sub(r"[^A-Za-z0-9_.-]", "_", r["url"].split("/data/")[1]) + ".txt"
        meta[k] = r
M = re.compile(r"(Dick[’'`]?s\b|DICK[’']S|Golf Galaxy|House of Sport|Field House)")
BAD = re.compile(r"Last Resort|Drive[- ]In|Wings|Dick[’']?s (?:Pizza|Restaurant|Sporting Goods, Inc\.? (?:\(|is|was|operates|NYSE))|Dick Clark|Smokehouse", re.I)
SALES = re.compile(r"(sales|per square foot|PSF|occupancy cost)", re.I)
DOLLAR = re.compile(r"\$\s?[\d,]{2,}")
HDR = re.compile(r"(Tenant Sales|Sales History|Sales PSF|Sales Per|Occupancy Cost|Occ\. Cost|TTM|Historical Sales|In-Line Sales|Major Tenant|Anchor)", re.I)
PROP = re.compile(r"(?:No\.\s?\d{1,2}\s?[–-]\s?|Loan #?\d+\s?[–-]\s?)([A-Z][^.$]{2,70}?)\s+(?:The following|Mortgage Loan Information|Mortgaged Property Information|Market Overview|Historical|Cash Flow|Underwritten|Tenant Summary)")
out = open(os.path.join(RAW, "B10_review.txt"), "w", encoding="utf-8")
ndocs = 0
for fn in sorted(os.listdir(C3)):
    if fn not in meta: continue
    t = open(os.path.join(C3, fn), encoding="utf-8", errors="ignore").read()
    m0 = meta.get(fn, {})
    items, seen = [], set()
    for m in M.finditer(t):
        a = t[max(0, m.start() - 350): m.start() + 450]
        after = t[m.start(): m.start() + 300]
        if BAD.search(t[m.start(): m.start() + 60]):
            continue
        if not (SALES.search(a) and DOLLAR.search(after[:260] + t[max(0, m.start() - 200): m.start()])):
            continue
        k = re.sub(r"\W", "", t[m.start(): m.start() + 200])
        if k in seen:
            continue
        seen.add(k)
        back = t[max(0, m.start() - 2500): m.start()]
        hm = list(HDR.finditer(back))
        hdr = back[hm[-1].start():][-500:] if hm else ""
        pm = list(PROP.finditer(t[max(0, m.start() - 80000): m.start()]))
        prop = pm[-1].group(1) if pm else ""
        items.append((m.start(), prop, hdr, t[max(0, m.start() - 250): m.start() + 420]))
    if not items:
        continue
    ndocs += 1
    out.write(f"\n######## {m0.get('file_date')} | {m0.get('form')} | {m0.get('filer','')[:60]} | {m0.get('url')}\n")
    for pos, prop, hdr, ctx in items:
        out.write(f"-- @{pos} PROP: {prop}\n   HDR: {hdr}\n   CTX: {ctx}\n")
out.close()
print("docs with items", ndocs)
