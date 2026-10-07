"""D01 helper: fetch a public URL and print visible text (optionally grep lines).
Rerun: python D01_fetch.py <url> [regex] [maxchars]
Saves nothing unless D01_SAVE env var is set to a file path.
"""
import os
import re
import sys

import requests
from bs4 import BeautifulSoup

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9"}


def fetch(url):
    r = requests.get(url, headers=UA, timeout=40)
    ct = r.headers.get("content-type", "")
    if "pdf" in ct or url.lower().endswith(".pdf"):
        return r.status_code, "[PDF bytes %d]" % len(r.content), r.content
    soup = BeautifulSoup(r.text, "html.parser")
    for t in soup(["script", "style", "noscript"]):
        t.decompose()
    txt = re.sub(r"\n\s*\n+", "\n", soup.get_text("\n"))
    return r.status_code, txt, r.content


if __name__ == "__main__":
    url = sys.argv[1]
    pat = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != "-" else None
    mx = int(sys.argv[3]) if len(sys.argv) > 3 else 15000
    code, txt, raw = fetch(url)
    print("HTTP", code)
    if os.environ.get("D01_SAVE"):
        with open(os.environ["D01_SAVE"], "w", encoding="utf-8") as f:
            f.write(txt)
    if pat:
        lines = [l for l in txt.splitlines() if re.search(pat, l, re.I)]
        print("\n".join(lines)[:mx])
    else:
        print(txt[:mx])
