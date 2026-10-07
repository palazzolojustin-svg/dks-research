"""B8 wave3: extract every DICK'S / Golf Galaxy / HoS / FH store-SALES datapoint (sentences + sales-history table rows)
from all cached CMBS docs (raw/H04_edgar_cache + raw/B8_cache). Output: raw/B8_sales_candidates.txt grouped by property.
Rerun: python B8_panel_extract.py
"""
import os, re, csv, glob
RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw"
files = glob.glob(os.path.join(RAW, "H04_edgar_cache", "*.txt")) + glob.glob(os.path.join(RAW, "B8_cache", "*.txt"))
meta = {}
for fn in ["H04_dkssales_OCCR_hits.csv", "H04_dkssales_OCC_hits.csv", "H04_dkssales_HOSPSF_hits.csv", "B8_hits.csv", "B8_hits_q2.csv"]:
    p = os.path.join(RAW, fn)
    if os.path.exists(p):
        for r in csv.DictReader(open(p, encoding="utf-8")):
            try:
                k = re.sub(r"[^A-Za-z0-9_.-]", "_", r["url"].split("/data/")[1]) + ".txt"
            except Exception:
                continue
            meta[k] = (r.get("file_date", ""), r.get("form", ""), r["url"])
NAME = r"(?:Dick[’'`]s|Dicks\b|DICK[’']S|Golf Galaxy|House of Sport|Field House)"
SENT = re.compile(NAME + r"[^.]{0,250}?(?:sales|Sales)[^.]{0,300}?\$\s?[\d,.]+[^.]{0,250}")
SENT2 = re.compile(r"(?:sales|Sales)[^.]{0,200}?" + NAME + r"[^.]{0,250}?\$\s?[\d,.]+[^.]{0,200}")
ROW = re.compile(NAME + r"[^$]{0,60}(?:\$\s?[\d,]+(?:\.\d+)?\s*(?:\(\d\)\s*)?){2,}")
PROP = re.compile(r"No\.\s?\d{1,2}\s?[–-]\s?([A-Z][^.$]{2,60}?)\s+(?:The following|Mortgage Loan Information|Mortgaged Property Information|Market Overview|Historical|Cash Flow|Underwritten|Major Tenants|Tenant Summary|Sales|Anchor)")
BAD = re.compile(r"\$12\.4 billion|net sales of \$1[0-9]\.\d billion|Dickinson|Dick[’']s (?:Pizza|Restaurant|Last)|Dick Clark|Sale Price", re.I)
out = {}
for fp in sorted(files):
    k = os.path.basename(fp)
    t = open(fp, encoding="utf-8", errors="ignore").read()
    if not re.search(NAME, t): continue
    d = meta.get(k, ("", "", k))
    for rx, kind in [(SENT, "S"), (SENT2, "S"), (ROW, "R")]:
        for m in rx.finditer(t):
            s = re.sub(r"\s+", " ", m.group(0))[:600]
            if BAD.search(s): continue
            if kind == "R":
                hb = t[max(0, m.start() - 1500): m.start()]
                hm = list(re.finditer(r"(Sales|SALES)", hb))
                if not hm: continue
                hdr = re.sub(r"\s+", " ", hb[hm[-1].start() - 300 if hm[-1].start() > 300 else 0:])[-700:]
                if not re.search(r"20[12]\d|TTM|T-12", hdr): continue
                s = "HDR: " + hdr + " || ROW: " + s
            back = t[max(0, m.start() - 80000): m.start()]
            pm = list(PROP.finditer(back)); prop = pm[-1].group(1).strip() if pm else "?"
            key = (prop.lower()[:25], re.sub(r"\W", "", s[-300:])[:200])
            if key in out: continue
            out[key] = (prop, d[0], d[1], d[2], kind, s)
rows = sorted(out.values(), key=lambda r: (r[0].lower(), r[1]))
with open(os.path.join(RAW, "B8_sales_candidates.txt"), "w", encoding="utf-8") as f:
    for r in rows:
        f.write(f"## {r[0]} | {r[1]} {r[2]} | {r[3]}\n{r[4]}: {r[5]}\n\n")
print(len(files), "docs", len(rows), "candidates")
