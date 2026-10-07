"""X13: fast re-extraction of private-brand sentences from the EDGAR cache built by
X13_edgar_privatebrand_history.py (regex tag-strip instead of BeautifulSoup).

Rerun: python X13_extract_fast.py [CIK ...]   (default: all cached filings)
Output: PB_SCRAPE/raw/X13_privatebrand_sentences_fast.csv
"""
import os, re, glob, csv, html, sys
HERE = os.path.dirname(os.path.abspath(__file__))
C = os.path.join(HERE, "..", "raw", "X13_edgar_cache")
OUT = os.path.join(HERE, "..", "raw", "X13_privatebrand_sentences_fast.csv")
PAT = re.compile(r"(private[- ]label|private[- ]brand|owned brand|own brand|exclusive brand|vertical brand|proprietary brand|kirkland signature|owned-brand|our brands|exclusive brands)", re.I)
NUM = re.compile(r"(\d+(\.\d+)?\s?%|\$\s?\d|percent|billion|one[- ]third|one[- ]quarter|one[- ]fifth)", re.I)
TK = {"1089063": "DKS", "1817358": "ASO", "1017480": "HIBB", "1156388": "BGFV", "1132105": "SPWH",
      "885639": "KSS", "27419": "TGT", "916365": "TSCO", "909832": "COST", "850209": "FL"}

def text(h):
    h = re.sub(r"(?is)<(script|style).*?</\1>", " ", h)
    h = re.sub(r"(?s)<[^>]+>", " ", h)
    return re.sub(r"\s+", " ", html.unescape(h))

def main(ciks):
    rows = []
    for f in sorted(glob.glob(os.path.join(C, "https___www_sec_gov_Archives_edgar_data_*"))):
        b = os.path.basename(f)
        m = re.match(r"https___www_sec_gov_Archives_edgar_data_(\d+)_(\d{18})_(.*)", b)
        if not m: continue
        cik, acc, doc = m.groups()
        if ciks and cik not in ciks: continue
        t = text(open(f, encoding="utf-8", errors="ignore").read())
        seen = set()
        for s in re.split(r"(?<=[.;])\s+(?=[A-Z])", t):
            if PAT.search(s) and NUM.search(s) and len(s) < 900 and s[:150] not in seen:
                seen.add(s[:150]); rows.append([TK.get(cik, cik), acc, doc, s.strip()])
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["ticker", "accession", "doc", "sentence"]); w.writerows(rows)
    print(len(rows), "rows ->", OUT, flush=True)

if __name__ == "__main__":
    main(set(sys.argv[1:]))
