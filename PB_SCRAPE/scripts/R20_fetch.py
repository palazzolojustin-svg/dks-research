"""R20_fetch.py  - fetch a URL (or several), print status + visible text, optionally only lines matching a regex.
Usage: python R20_fetch.py <url> [regex] [context_chars]
"""
import requests, re, sys
from bs4 import BeautifulSoup
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36",
     "Accept-Language": "en-US,en;q=0.9", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}


def fetch(url):
    r = requests.get(url, headers=H, timeout=40)
    return r


def text_of(html):
    s = BeautifulSoup(html, "html.parser")
    for t in s(["script", "style", "noscript"]):
        t.decompose()
    return re.sub(r"\s+", " ", s.get_text(" "))


if __name__ == "__main__":
    url = sys.argv[1]
    pat = sys.argv[2] if len(sys.argv) > 2 else None
    ctx = int(sys.argv[3]) if len(sys.argv) > 3 else 300
    r = fetch(url)
    print("STATUS", r.status_code, "LEN", len(r.text), "FINAL", r.url)
    t = text_of(r.text)
    if not pat:
        print(t[:ctx if ctx > 300 else 6000])
    else:
        for m in re.finditer(pat, t, re.I):
            print("...", t[max(0, m.start() - ctx):m.end() + ctx], "...\n")
