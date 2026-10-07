"""B3: fetch web pages, save text to raw/B3_<name>.txt and print paragraphs containing numbers/keywords.
Rerun: python B3_fetch.py <name> <url> [<name> <url> ...]
"""
import sys, os, re, requests
from bs4 import BeautifulSoup
RAW = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "raw")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"}
KW = re.compile(r"\$|million|sales|revenue|visit|traffic|employ|jobs|square|sq\.? ?f|open|tax|relocat|close|staff|percent|%", re.I)
a = sys.argv[1:]
for name, url in zip(a[0::2], a[1::2]):
    try:
        r = requests.get(url, headers=UA, timeout=60)
    except Exception as e:
        print("ERR", name, e); continue
    s = BeautifulSoup(r.text, "html.parser")
    for x in s(["script", "style", "nav", "footer", "header"]):
        x.decompose()
    paras = [p.get_text(" ", strip=True) for p in s.find_all(["p", "li", "h1", "h2", "h3"])]
    paras = [p for p in paras if len(p) > 30]
    txt = url + "\n" + "\n".join(paras)
    open(os.path.join(RAW, f"B3_{name}.txt"), "w", encoding="utf-8").write(txt)
    print(f"===== {name} HTTP {r.status_code} paras={len(paras)} {url}")
    for p in paras:
        if KW.search(p) and re.search(r"house of sport|dick|store|mall", p, re.I):
            print(" *", p[:700])
