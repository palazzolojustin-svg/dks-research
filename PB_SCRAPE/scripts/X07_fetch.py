"""X07 helper: fetch a URL with browser-like headers and print the visible text (optionally only around keywords).

Rerun:  python X07_fetch.py <url> [keyword1,keyword2] [window_chars]
Example: python X07_fetch.py https://mygolfspy.com/buyers-guides/golf-balls/2026-mygolfspy-golf-ball-test/ maxfli 600
Saves raw HTML to PB_SCRAPE\\raw\\X07_<slug>.html. Used for MyGolfSpy, Golf Monthly, golfWRX, Golf Galaxy pages.
No login, no CAPTCHA solving: if the site returns 403/challenge, the status is printed and nothing else is attempted.
"""
import re
import sys
import os
import requests
from bs4 import BeautifulSoup

H = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "raw")


def fetch(url):
    r = requests.get(url, headers=H, timeout=40)
    return r


def text_of(html):
    s = BeautifulSoup(html, "html.parser")
    for t in s(["script", "style", "noscript", "svg"]):
        t.decompose()
    return re.sub(r"\n{2,}", "\n", s.get_text("\n", strip=True))


if __name__ == "__main__":
    url = sys.argv[1]
    kws = sys.argv[2].split(",") if len(sys.argv) > 2 and sys.argv[2] else []
    win = int(sys.argv[3]) if len(sys.argv) > 3 else 500
    r = fetch(url)
    print("STATUS", r.status_code, len(r.content))
    slug = re.sub(r"[^A-Za-z0-9]+", "_", url.split("//", 1)[-1])[:90]
    with open(os.path.join(RAW, "X07_" + slug + ".html"), "wb") as f:
        f.write(r.content)
    t = text_of(r.text)
    if not kws:
        print(t[:20000])
    else:
        low = t.lower()
        spans = []
        for k in kws:
            for m in re.finditer(re.escape(k.lower()), low):
                spans.append((max(0, m.start() - win), min(len(t), m.end() + win)))
        spans.sort()
        merged = []
        for a, b in spans:
            if merged and a <= merged[-1][1]:
                merged[-1] = (merged[-1][0], max(b, merged[-1][1]))
            else:
                merged.append((a, b))
        for a, b in merged:
            print("-----", a)
            print(t[a:b])
