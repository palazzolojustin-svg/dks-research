"""P3: pull DKS ticket/transaction comp decomposition from 10-Q/10-K MD&A, FY2016-FY2022 (EDGAR).
Rerun: python THESIS_SCRAPE\\scripts\\P3_edgar_ticket.py
Output: raw\\P3_edgar_ticket_sentences.txt (every sentence mentioning transactions + ticket/sales per transaction, per filing)
"""
import re, time, requests
from bs4 import BeautifulSoup

UA = {"User-Agent": "DKS research palazzolojustin@gmail.com"}
OUT = r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\P3_edgar_ticket_sentences.txt"


def main():
    sub = requests.get("https://data.sec.gov/submissions/CIK0001089063.json", headers=UA, timeout=60).json()
    rec = sub["filings"]["recent"]
    rows = []
    for f, d, a, p, rd in zip(rec["form"], rec["filingDate"], rec["accessionNumber"], rec["primaryDocument"], rec["reportDate"]):
        if f in ("10-Q", "10-K") and "2016-03-01" <= d <= "2023-06-30":
            rows.append((f, d, a, p, rd))
    with open(OUT, "w", encoding="utf-8") as fo:
        for f, d, a, p, rd in sorted(rows, key=lambda x: x[1]):
            url = f"https://www.sec.gov/Archives/edgar/data/1089063/{a.replace('-', '')}/{p}"
            r = requests.get(url, headers=UA, timeout=90)
            txt = BeautifulSoup(r.content, "lxml").get_text(" ")
            txt = re.sub(r"\s+", " ", txt)
            sents = re.split(r"(?<=[.;])\s+", txt)
            hits = [s for s in sents if re.search(r"transactions", s, re.I) and re.search(r"ticket|per transaction|sales per", s, re.I) and re.search(r"\d", s)]
            fo.write(f"### {f} filed {d} period {rd} {url}\n")
            for s in hits[:8]:
                fo.write("- " + s.strip()[:600] + "\n")
            print(f, d, rd, len(hits))
            time.sleep(0.4)


if __name__ == "__main__":
    main()
