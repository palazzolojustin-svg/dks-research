"""X13: Pull every 10-K (and IPO S-1) for a set of retailers from SEC EDGAR and extract
sentences that quantify private-label / owned-brand / vertical-brand penetration.

Rerun:  python X13_edgar_privatebrand_history.py
Output: PB_SCRAPE/raw/X13_edgar_privatebrand_sentences.csv  (company, form, filing date, period, sentence)
Method: EDGAR submissions JSON (data.sec.gov) -> primary doc HTML -> text -> regex for
        (private label|private brand|owned brand|exclusive brand|vertical brand|proprietary brand|own brand|Kirkland|exclusive)
        within sentences that also contain a % or $ figure.
EDGAR asks for a descriptive User-Agent and <=10 req/s; we sleep 0.25s between calls.
"""
import re, time, csv, json, os, sys
import requests
from bs4 import BeautifulSoup

UA = {"User-Agent": "DKS research palazzolojustin@gmail.com"}
OUT = os.path.join(os.path.dirname(__file__), "..", "raw", "X13_edgar_privatebrand_sentences.csv")
CACHE = os.path.join(os.path.dirname(__file__), "..", "raw", "X13_edgar_cache")
os.makedirs(CACHE, exist_ok=True)

COMPANIES = {
    "DKS": 1089063, "ASO": 1817358, "HIBB": 1017480, "BGFV": 1156388, "SPWH": 1132105,
    "KSS": 885639, "TGT": 27419, "TSCO": 916365, "COST": 909832, "FL": 850209,
}
FORMS = {"10-K", "10-K405", "S-1", "S-1/A", "424B4"}
PAT = re.compile(r"(private[- ]label|private[- ]brand|owned brand|own brand|exclusive brand|vertical brand|proprietary brand|kirkland|owned-brand|our brands)", re.I)
NUM = re.compile(r"(\d+(\.\d+)?\s?%|\$\s?\d|percent|billion|one[- ]third|one[- ]quarter|one[- ]fifth)", re.I)


def get(url):
    fn = os.path.join(CACHE, re.sub(r"[^A-Za-z0-9]", "_", url)[-180:])
    if os.path.exists(fn):
        return open(fn, encoding="utf-8", errors="ignore").read()
    time.sleep(0.25)
    r = requests.get(url, headers=UA, timeout=60)
    r.raise_for_status()
    open(fn, "w", encoding="utf-8").write(r.text)
    return r.text


def filings(cik):
    d = json.loads(get(f"https://data.sec.gov/submissions/CIK{cik:010d}.json"))
    rows = []
    def add(f):
        for i, form in enumerate(f["form"]):
            if form in FORMS:
                rows.append((form, f["filingDate"][i], f.get("reportDate", [""] * len(f["form"]))[i], f["accessionNumber"][i], f["primaryDocument"][i]))
    add(d["filings"]["recent"])
    for extra in d["filings"].get("files", []):
        add(json.loads(get("https://data.sec.gov/submissions/" + extra["name"])))
    return rows


def sentences(html):
    t = BeautifulSoup(html, "html.parser").get_text(" ")
    t = re.sub(r"\s+", " ", t)
    return re.split(r"(?<=[.;])\s+(?=[A-Z])", t)


def main(only=None):
    out = []
    for tk, cik in COMPANIES.items():
        if only and tk not in only:
            continue
        try:
            fl = filings(cik)
        except Exception as e:
            print(tk, "ERR", e); continue
        for form, fdate, rdate, acc, doc in fl:
            if not doc:
                continue
            url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc.replace('-', '')}/{doc}"
            try:
                html = get(url)
            except Exception as e:
                print(tk, fdate, "ERR", e); continue
            seen = set()
            for s in sentences(html):
                if PAT.search(s) and NUM.search(s) and len(s) < 900:
                    k = s[:200]
                    if k in seen: continue
                    seen.add(k)
                    out.append([tk, form, fdate, rdate, s.strip()])
            print(tk, form, fdate, "done")
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["ticker", "form", "filing_date", "period", "sentence"]); w.writerows(out)
    print("rows", len(out), "->", OUT)


if __name__ == "__main__":
    main(set(sys.argv[1:]) or None)
