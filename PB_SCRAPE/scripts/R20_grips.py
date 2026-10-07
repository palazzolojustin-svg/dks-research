"""R20_grips.py - pull Grips Intelligence public retailer insight page (free, no login) for a retailer domain and dump
embedded data: text, __NEXT_DATA__/JSON blobs, any brand / category / revenue / traffic numbers.
Usage: python R20_grips.py dickssportinggoods.com [academy.com ...]
Output: PB_SCRAPE/raw/R20_grips_<domain>.html and .txt
"""
import requests, re, sys, os, json
from bs4 import BeautifulSoup
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"}
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "raw")
for d in sys.argv[1:]:
    u = f"https://gripsintelligence.com/insights/retailers/{d}"
    r = requests.get(u, headers=H, timeout=40)
    open(os.path.join(RAW, f"R20_grips_{d}.html"), "w", encoding="utf-8").write(r.text)
    s = BeautifulSoup(r.text, "html.parser")
    for t in s(["script", "style", "noscript"]):
        pass
    txt = re.sub(r"\s+", " ", BeautifulSoup(r.text, "html.parser").get_text(" "))
    open(os.path.join(RAW, f"R20_grips_{d}.txt"), "w", encoding="utf-8").write(txt)
    print("==", d, r.status_code, len(r.text), "text", len(txt))
    print(txt[:4000])
    scripts = [x.string or "" for x in s.find_all("script")]
    big = sorted(scripts, key=len, reverse=True)[:3]
    for b in big:
        print("-- script len", len(b), b[:600].replace("\n", " "))
