"""B8: extract DICK'S tenant rows (sales / sales PSF / occupancy cost) from cached CMBS docs, with property name + table header.
Rerun: python B8_extract_rows.py  -> raw/B8_rows_raw.tsv (one row per unique DICK'S table row) and raw/B8_rows_review.txt
"""
import os, re, csv, glob
RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw"
files = glob.glob(os.path.join(RAW, "H04_edgar_cache", "*.txt")) + glob.glob(os.path.join(RAW, "B8_cache", "*.txt"))
meta = {}
for fn in ["H04_dkssales_OCCR_hits.csv", "H04_dkssales_OCC_hits.csv", "H04_dkssales_HOSPSF_hits.csv", "B8_hits.csv"]:
    p = os.path.join(RAW, fn)
    if os.path.exists(p):
        for r in csv.DictReader(open(p, encoding="utf-8")):
            k = re.sub(r"[^A-Za-z0-9_.-]", "_", r["url"].split("/data/")[1]) + ".txt"
            meta[k] = (r["file_date"], r["form"], r["filer"], r["url"])
M = re.compile(r"(Dick[’'`]s|Dicks\b|DICK[’']S|Golf Galaxy|House of Sport|Field House)")
BAD = re.compile(r"Last Resort|Drive[- ]In|Wings|Dick[’']s (?:Pizza|Restaurant)|Dick Clark", re.I)
NUM = re.compile(r"\$\s?[\d,]{3,}|\d{1,3}\.\d\s?%")
PROP = re.compile(r"No\.\s?\d{1,2}\s?[–-]\s?([A-Z][^.$]{2,70}?)\s+(?:The following|Mortgage Loan Information|Mortgaged Property Information|Market Overview|Historical|Cash Flow|Underwritten)")
PROP2 = re.compile(r"\bthe ([A-Z][A-Za-z0-9’'&\.\-, ]{2,60}?) Propert(?:y|ies)\b")
HDR = re.compile(r"(Tenant Sales|Sales History|Top Tenant|Major Tenant|Tenant Name|Anchor|Comparable|Competitive|Retail Comparables|Sales PSF|Occupancy Cost)", re.I)
rows, seen = [], set()
for fp in sorted(files):
    k = os.path.basename(fp)
    t = open(fp, encoding="utf-8", errors="ignore").read()
    for m in M.finditer(t):
        after = t[m.start(): m.start() + 330]
        if BAD.search(after[:60]): continue
        if not NUM.search(after[:200]): continue
        row = re.sub(r"\s+", " ", after)
        nk = re.sub(r"\W", "", row[:160])
        if nk in seen: continue
        seen.add(nk)
        back = t[max(0, m.start() - 60000): m.start()]
        pm = list(PROP.finditer(back)); p1 = pm[-1].group(1) if pm else ""
        pm2 = [x.group(1) for x in PROP2.finditer(back[-20000:]) if not re.match(r"(Mortgaged|Related|Underlying|Subject|Retail|Office|Hotel|Industrial|Multifamily|Mixed|Real|Single|Collateral)$", x.group(1))]
        p2 = pm2[-1] if pm2 else ""
        hb = t[max(0, m.start() - 900): m.start()]
        hm = list(HDR.finditer(hb)); hdr = hb[hm[-1].start():] if hm else hb[-300:]
        d = meta.get(k, ("", "", "", ""))
        rows.append([d[0], d[1], d[2][:50], k, p1, p2, re.sub(r"\s+", " ", hdr)[-600:], row])
with open(os.path.join(RAW, "B8_rows_raw.tsv"), "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter="\t"); w.writerow(["file_date", "form", "filer", "doc", "prop_no", "prop_the", "header", "row"])
    rows.sort(key=lambda r: (r[4] or r[5], r[0]))
    w.writerows(rows)
with open(os.path.join(RAW, "B8_rows_review.txt"), "w", encoding="utf-8") as f:
    for r in rows:
        f.write(f"### {r[0]} {r[1]} | {r[2]} | {r[3]}\nPROP: {r[4]} || {r[5]}\nHDR: {r[6][-450:]}\nROW: {r[7]}\n\n")
print(len(files), "docs", len(rows), "rows")
