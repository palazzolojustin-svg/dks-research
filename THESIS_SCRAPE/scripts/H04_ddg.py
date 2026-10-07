"""H04: lightweight web search via DuckDuckGo's public HTML endpoint (used after the WebSearch tool budget ran out).
Stops (no retry) if a challenge/captcha page is returned.

Rerun: python H04_ddg.py "query" [max_results]
"""
import sys
import time
import urllib.parse
import requests
from bs4 import BeautifulSoup

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"}


def search(q, n=10):
    r = requests.post("https://html.duckduckgo.com/html/", data={"q": q}, headers=UA, timeout=30)
    if "captcha" in r.text.lower() or "anomaly" in r.text.lower():
        print("BLOCKED/CHALLENGE - stopping")
        return []
    soup = BeautifulSoup(r.text, "html.parser")
    out = []
    for res in soup.select(".result")[:n]:
        a = res.select_one("a.result__a")
        if not a:
            continue
        href = a.get("href", "")
        if "uddg=" in href:
            href = urllib.parse.unquote(href.split("uddg=")[1].split("&")[0])
        snip = res.select_one(".result__snippet")
        out.append((a.get_text(" ", strip=True), href, snip.get_text(" ", strip=True) if snip else ""))
    return out


if __name__ == "__main__":
    for qq in sys.argv[1].split("||"):
        print("=== Q:", qq)
        for t, h, s in search(qq, int(sys.argv[2]) if len(sys.argv) > 2 else 10):
            print("-", t, "|", h, "\n   ", s[:400])
        time.sleep(3)
