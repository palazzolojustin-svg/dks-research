"""P5: fetch article URLs (plain requests, then curl_cffi fallback), save cleaned text to raw\\P5_pages\\<slug>.txt.
Rerun: python THESIS_SCRAPE\\scripts\\P5_fetch.py URL [URL ...]   (prints status, length and the path)
Optional: python P5_fetch.py --grep "regex" URL ...  -> prints matching sentences.
"""
import os, re, sys, hashlib, urllib.parse
import requests
from bs4 import BeautifulSoup

OUT = r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\P5_pages"
os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9"}


def unwrap(u):
    if "bing.com/news/apiclick" in u:
        q = urllib.parse.parse_qs(urllib.parse.urlparse(u).query)
        return q.get("url", [u])[0]
    return u


def fetch(u):
    try:
        r = requests.get(u, headers=UA, timeout=40)
        if r.status_code == 200 and len(r.content) > 2000:
            return r.status_code, r.content
        st = r.status_code
    except Exception as e:
        st = str(e)[:80]
    try:
        from curl_cffi import requests as cr
        r = cr.get(u, impersonate="chrome", timeout=40)
        return r.status_code, r.content
    except Exception as e:
        return f"{st} / cffi {str(e)[:60]}", b""


def main():
    args = sys.argv[1:]
    pat = None
    if args and args[0] == "--grep":
        pat = re.compile(args[1], re.I); args = args[2:]
    for u in args:
        u = unwrap(u)
        st, html = fetch(u)
        soup = BeautifulSoup(html, "lxml")
        for t in soup(["script", "style", "nav", "footer", "header"]):
            t.decompose()
        txt = re.sub(r"\s+", " ", soup.get_text(" "))
        slug = re.sub(r"[^A-Za-z0-9]+", "_", urllib.parse.urlparse(u).netloc + urllib.parse.urlparse(u).path)[:120]
        p = os.path.join(OUT, slug + ".txt")
        open(p, "w", encoding="utf-8").write(u + "\n" + txt)
        print("##", st, len(txt), p)
        if pat:
            for s in re.split(r"(?<=[.!?])\s+", txt):
                if pat.search(s) and len(s) < 1200:
                    print("  -", s)


if __name__ == "__main__":
    main()
