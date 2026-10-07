"""H03: lightweight web search via Bing HTML (fallback when the WebSearch tool budget is exhausted).
Rerun: python H03_search.py "query" [max]      or      python H03_search.py -f queries.txt [max]
(-f: one query per line; avoids PowerShell 5.1 stripping embedded double quotes.)
Prints title | url | snippet. Does not retry or evade if a challenge page is returned.
"""
import sys, time, requests, base64, urllib.parse
from bs4 import BeautifulSoup

if sys.argv[1] == "-f":
    queries = [l.strip() for l in open(sys.argv[2], encoding="utf-8") if l.strip()]
    mx = int(sys.argv[3]) if len(sys.argv) > 3 else 10
else:
    queries = [sys.argv[1]]; mx = int(sys.argv[2]) if len(sys.argv) > 2 else 12
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9"}


def real(href):
    if "bing.com/ck/a" in href and "u=a1" in href:
        u = urllib.parse.parse_qs(urllib.parse.urlparse(href).query).get("u", [""])[0][2:]
        try:
            return base64.urlsafe_b64decode(u + "=" * (-len(u) % 4)).decode("utf-8", "ignore")
        except Exception:
            return href
    return href


for q in queries:
    print("### Q:", q)
    r = requests.get("https://www.bing.com/search", params={"q": q, "count": "20", "setlang": "en-US", "cc": "US"}, headers=UA, timeout=60)
    s = BeautifulSoup(r.text, "html.parser")
    res = s.select("li.b_algo")
    if not res:
        print("NO RESULTS / possibly blocked; status", r.status_code)
    for li in res[:mx]:
        a = li.select_one("h2 a")
        if not a: continue
        p = li.select_one("p") or li.select_one(".b_caption")
        print("-", a.get_text(" ", strip=True)[:110], "|", real(a["href"]), "|", (p.get_text(" ", strip=True) if p else "")[:280])
    time.sleep(2)
