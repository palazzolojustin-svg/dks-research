"""H04 helper: fetch a URL, convert to text, save raw text, print keyword-matching passages.

Rerun: python H04_fetch_grep.py <url> <raw_name> [regex]
  - saves text to THESIS_SCRAPE/raw/H04_<raw_name>.txt
  - prints paragraphs/sentences matching regex (default: Dick|House of Sport|Field House|sporting goods)
"""
import re
import sys
import os
import requests
from bs4 import BeautifulSoup

RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9"}


def fetch_text(url):
    hdr = {"User-Agent": "IndependentResearch research-script contact@example.org"} if "sec.gov" in url else UA
    r = requests.get(url, headers=hdr, timeout=90)
    ct = r.headers.get("content-type", "")
    if "pdf" in ct or url.lower().endswith(".pdf"):
        import io
        import pdfplumber
        with pdfplumber.open(io.BytesIO(r.content)) as pdf:
            return r.status_code, "\n".join((p.extract_text() or "") for p in pdf.pages)
    soup = BeautifulSoup(r.text, "html.parser")
    for t in soup(["script", "style", "noscript"]):
        t.decompose()
    txt = soup.get_text("\n")
    txt = re.sub(r"\n\s*\n+", "\n", txt)
    return r.status_code, txt


def main():
    url, name = sys.argv[1], sys.argv[2]
    pat = sys.argv[3] if len(sys.argv) > 3 else r"Dick|House of Sport|Field House|sporting goods"
    code, txt = fetch_text(url)
    path = os.path.join(RAW, f"H04_{name}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(url + "\n" + txt)
    print("STATUS", code, "chars", len(txt), "->", path)
    lines = txt.split("\n")
    rx = re.compile(pat, re.I)
    shown = set()
    for i, ln in enumerate(lines):
        if rx.search(ln):
            for j in range(max(0, i - 1), min(len(lines), i + 2)):
                if j not in shown:
                    shown.add(j)
                    print(f"[{j}] {lines[j].strip()[:1500]}")
            print("---")


if __name__ == "__main__":
    main()
