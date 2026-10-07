"""N3: ASO private-label disclosure wording tracker (10-K/10-Q year over year).

Rerun: python PB_SCRAPE\\scripts\\N3_aso_pl_wording.py
Reads cached ASO EDGAR filings in PB_SCRAPE\\raw\\X13_edgar_cache (pulled by X13's script) plus the
folder SOURCE copies of the FY25 10-K and FY25Q3/FY26Q1/FY26Q2 10-Qs, strips HTML, and prints every
sentence mentioning private label / private brand penetration, customer reach, brand count and the
"more units of our private label ... adverse impact on our total net sales" mix sentence.
Output: PB_SCRAPE\\raw\\N3_aso_pl_wording.csv (file, sentence).
To extend weekly/quarterly: add new ASO 10-Q/10-K URLs to EXTRA_URLS (EDGAR needs a User-Agent header).
"""
import csv, glob, html, os, re, sys

ROOT = r"C:\Users\palaz\Downloads\DKS_RESEARCH"
CACHE = os.path.join(ROOT, r"PB_SCRAPE\raw\X13_edgar_cache")
SRC = os.path.join(ROOT, r"SOURCE\04_PEERS\ASO\sec_filings")
OUT = os.path.join(ROOT, r"PB_SCRAPE\raw\N3_aso_pl_wording.csv")

PATS = [
    r"private (label|brand)[^.]{0,200}(\d+%|percent)",
    r"(\d+%|percent)[^.]{0,200}private (label|brand)",
    r"national brand (products|merchandise)[^.]{0,80}\d+%",
    r"\d+%[^.]{0,80}national brand",
    r"more units of our private label",
    r"portfolio of \d+ private",
    r"\d+ private label brands",
    r"customers purchased a private",
]
rx = re.compile("|".join(PATS), re.I)


def clean(t):
    t = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", t)
    t = re.sub(r"<[^>]+>", " ", t)
    t = html.unescape(t)
    return re.sub(r"\s+", " ", t)


def sentences(t):
    return re.split(r"(?<=[.;])\s+(?=[A-Z\u2022])", t)


def main():
    files = sorted(glob.glob(os.path.join(CACHE, "*1817358*")))
    files = [f for f in files if "submissions" not in f]
    files += sorted(glob.glob(os.path.join(SRC, "*.md")))
    rows = []
    for f in files:
        try:
            t = open(f, encoding="utf-8", errors="ignore").read()
        except Exception as e:
            print("skip", f, e)
            continue
        t = clean(t)
        seen = set()
        for s in sentences(t):
            if len(s) > 1500:
                # long run without sentence breaks: window around matches
                for m in rx.finditer(s):
                    w = s[max(0, m.start() - 250): m.end() + 250]
                    if w not in seen:
                        seen.add(w); rows.append((os.path.basename(f), w))
                continue
            if rx.search(s) and s not in seen:
                seen.add(s); rows.append((os.path.basename(f), s.strip()))
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["file", "sentence"]); w.writerows(rows)
    for fn, s in rows:
        print(f"[{fn[-60:]}] {s[:400]}")
    print(len(rows), "rows ->", OUT)


if __name__ == "__main__":
    main()
