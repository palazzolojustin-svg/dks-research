"""P5: peer-retailer comp decomposition (ticket / transactions / traffic / AUR / units) from SEC EDGAR.

For each peer CIK, pulls every 10-Q / 10-K filed in [START, END] plus 8-K EX-99.x earnings releases,
strips HTML, and saves every sentence that mentions ticket / transactions / traffic / AUR / units / ASP.
Rerun: python THESIS_SCRAPE\\scripts\\P5_edgar_peer_ticket.py [START] [END] [TICKER,TICKER...]
Output: raw\\P5_edgar_sentences.jsonl (one row per sentence), raw\\P5_edgar_cache\\*.txt (cleaned docs)
"""
import json, os, re, sys, time
import requests
from bs4 import BeautifulSoup

UA = {"User-Agent": "DKS research palazzolojustin@gmail.com", "Accept-Encoding": "gzip, deflate"}
BASE = r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw"
CACHE = os.path.join(BASE, "P5_edgar_cache")
os.makedirs(CACHE, exist_ok=True)
OUT = os.path.join(BASE, "P5_edgar_sentences.jsonl")

PEERS = {
    "ASO": 1817358, "TGT": 27419, "WMT": 104169, "TSCO": 916365, "FL": 850209, "HIBB": 1017480,
    "BGFV": 1156388, "GCO": 18498, "SCVL": 895447, "BOOT": 1610250, "SPWH": 1132105,
    "HD": 354950, "LOW": 60667, "DG": 29534, "DLTR": 935703, "ULTA": 1403568, "FIVE": 1177609,
    "OLLI": 1639300, "DBI": 1319947, "BURL": 1579298, "COST": 909832, "BJ": 1531152,
}
START = sys.argv[1] if len(sys.argv) > 1 else "2024-01-01"
END = sys.argv[2] if len(sys.argv) > 2 else "2026-10-07"
ONLY = set(sys.argv[3].split(",")) if len(sys.argv) > 3 else None

PAT = re.compile(r"(average ticket|avg\.? ticket|ticket|comparable transactions|number of transactions|customer transactions|"
                 r"transaction count|traffic|average unit retail|\bAUR\b|units per transaction|average selling price|"
                 r"average transaction (amount|size|value)|average sale|basket)", re.I)


def get(url):
    for i in range(4):
        try:
            r = requests.get(url, headers=UA, timeout=60)
            if r.status_code == 200:
                return r
            if r.status_code in (403, 404):
                return None
        except Exception as e:
            print("err", url, e, flush=True)
        time.sleep(1.5 * (i + 1))
    return None


def clean(html):
    t = BeautifulSoup(html, "lxml").get_text(" ")
    return re.sub(r"\s+", " ", t)


def filings(cik):
    sub = get(f"https://data.sec.gov/submissions/CIK{cik:010d}.json").json()
    rec = sub["filings"]["recent"]
    rows = list(zip(rec["form"], rec["filingDate"], rec["accessionNumber"], rec["primaryDocument"], rec["reportDate"]))
    return [r for r in rows if r[0] in ("10-Q", "10-K", "8-K") and START <= r[1] <= END]


def exhibits(cik, acc):
    idx = get(f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc.replace('-', '')}/index.json")
    if not idx:
        return []
    items = idx.json().get("directory", {}).get("item", [])
    return [it["name"] for it in items if re.search(r"(ex|exhibit)[-_]?99", it["name"], re.I) and it["name"].lower().endswith((".htm", ".html"))]


def main():
    done = set()
    if os.path.exists(OUT):
        for line in open(OUT, encoding="utf-8"):
            d = json.loads(line)
            done.add(d["url"])
    fo = open(OUT, "a", encoding="utf-8")
    for tk, cik in PEERS.items():
        if ONLY and tk not in ONLY:
            continue
        try:
            rows = filings(cik)
        except Exception as e:
            print("submissions fail", tk, e); continue
        print(tk, len(rows), "filings", flush=True)
        for form, fdate, acc, doc, rdate in rows:
            docs = [doc] if form in ("10-Q", "10-K") else exhibits(cik, acc)
            time.sleep(0.15)
            for d in docs:
                url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc.replace('-', '')}/{d}"
                if url in done:
                    continue
                r = get(url)
                time.sleep(0.15)
                if not r:
                    continue
                txt = clean(r.content)
                if form == "8-K" and not re.search(r"comparable|same.store|comp sales", txt, re.I):
                    continue
                with open(os.path.join(CACHE, f"{tk}_{fdate}_{form}_{d}.txt"), "w", encoding="utf-8") as fc:
                    fc.write(txt)
                sents = re.split(r"(?<=[.;])\s+", txt)
                n = 0
                for s in sents:
                    if PAT.search(s) and len(s) < 900 and re.search(r"\d", s):
                        fo.write(json.dumps(dict(tk=tk, form=form, filed=fdate, period=rdate, url=url, s=s)) + "\n")
                        n += 1
                fo.flush()
                print(" ", tk, form, fdate, d, n, flush=True)


if __name__ == "__main__":
    main()
