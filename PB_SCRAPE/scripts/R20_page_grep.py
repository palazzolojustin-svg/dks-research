"""R20_page_grep.py
Given a vendor sitemap (or a txt list of URLs) and a URL-slug regex, fetch every matching page and grep its visible text
for DKS / owned-brand terms. Prints hits with context; saves PB_SCRAPE/raw/R20_pagegrep_<tag>.csv
Usage: python R20_page_grep.py <sitemap_url_or_txtfile> <slug_regex> <tag> [text_regex]
Example: python R20_page_grep.py https://www.yipitdata.com/sitemap.xml "resources|blog" yipit
"""
import requests, re, sys, csv, os, time
from bs4 import BeautifulSoup
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"}
TXT = re.compile(sys.argv[4] if len(sys.argv) > 4 else
                 r"Dick'?s Sporting|DICK'?S|\bDKS\b|CALIA|VRST|Maxfli|Golf Galaxy|private[- ]label|owned brand|store brand|in-house brand", re.I)
src, slug, tag = sys.argv[1], re.compile(sys.argv[2], re.I), sys.argv[3]
if src.startswith("http"):
    x = requests.get(src, headers=H, timeout=40).text
    urls = re.findall(r"<loc>\s*(.*?)\s*</loc>", x)
    if "<sitemapindex" in x:
        kids = urls; urls = []
        for k in kids:
            try:
                urls += re.findall(r"<loc>\s*(.*?)\s*</loc>", requests.get(k, headers=H, timeout=40).text)
            except Exception:
                pass
else:
    urls = [l.strip() for l in open(src, encoding="utf-8") if l.strip()]
urls = [u for u in dict.fromkeys(urls) if slug.search(u)]
print(len(urls), "candidate urls")
rows = []
for i, u in enumerate(urls):
    try:
        r = requests.get(u, headers=H, timeout=40)
    except Exception as e:
        print("ERR", u, e); continue
    s = BeautifulSoup(r.text, "html.parser")
    for t in s(["script", "style", "noscript", "nav", "footer", "header"]):
        t.decompose()
    t = re.sub(r"\s+", " ", s.get_text(" "))
    ms = list(TXT.finditer(t))
    if ms:
        terms = sorted({m.group(0).lower() for m in ms})
        ctx = " || ".join(t[max(0, m.start() - 200):m.end() + 200] for m in ms[:6])
        rows.append([u, r.status_code, len(ms), ";".join(terms), ctx])
        print(f"HIT {len(ms):3d} {u} {terms}")
    time.sleep(0.4)
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "raw", f"R20_pagegrep_{tag}.csv")
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["url", "status", "n_hits", "terms", "context"]); w.writerows(rows)
print(len(rows), "pages with hits ->", out)
