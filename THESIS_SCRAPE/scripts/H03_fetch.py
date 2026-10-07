"""H03 helper: fetch a URL (HTML or PDF) and print/save its text.
Rerun: python H03_fetch.py <url> [outname] [grep_regex]
 - HTML -> visible text via BeautifulSoup; PDF -> text via pdfplumber (if installed) else pypdf.
 - Saves text to THESIS_SCRAPE/raw/H03_<outname>.txt when outname given.
 - If grep_regex given, prints only matching lines with +-2 lines of context.
"""
import sys, re, io, os
import requests
from bs4 import BeautifulSoup

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9"}
RAW = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "raw")


def fetch_text(url):
    r = requests.get(url, headers=UA, timeout=60)
    r.raise_for_status()
    ct = r.headers.get("content-type", "")
    if "pdf" in ct or url.lower().split("?")[0].endswith(".pdf") or r.content[:4] == b"%PDF":
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(r.content)) as pdf:
                return "\n".join((p.extract_text() or "") for p in pdf.pages)
        except ImportError:
            from pypdf import PdfReader
            rd = PdfReader(io.BytesIO(r.content))
            return "\n".join((p.extract_text() or "") for p in rd.pages)
    soup = BeautifulSoup(r.text, "html.parser")
    for t in soup(["script", "style", "noscript"]):
        t.decompose()
    txt = soup.get_text("\n")
    return re.sub(r"\n\s*\n+", "\n", txt)


if __name__ == "__main__":
    url = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != "-" else None
    pat = sys.argv[3] if len(sys.argv) > 3 else None
    txt = fetch_text(url)
    if out:
        with open(os.path.join(RAW, f"H03_{out}.txt"), "w", encoding="utf-8") as f:
            f.write(url + "\n\n" + txt)
    if pat:
        lines = txt.splitlines()
        rx = re.compile(pat, re.I)
        shown = set()
        for i, l in enumerate(lines):
            if rx.search(l):
                for j in range(max(0, i - 2), min(len(lines), i + 3)):
                    if j not in shown:
                        print(f"{j}: {lines[j]}")
                        shown.add(j)
                print("--")
    else:
        sys.stdout.reconfigure(encoding="utf-8")
        print(txt[:20000])
