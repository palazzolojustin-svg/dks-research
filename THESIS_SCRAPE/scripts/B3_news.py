"""B3: Bing News RSS + Google News RSS search helper. Prints date | source | title | url.
Rerun: python B3_news.py "<query>" ["<query>" ...]   (appends to raw/B3_news.csv)
"""
import sys, os, csv, time, requests, html, re
import xml.etree.ElementTree as ET
from urllib.parse import quote_plus, urlparse, parse_qs
RAW = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "raw")
UA = {"User-Agent": "Mozilla/5.0 (research)"}
out = open(os.path.join(RAW, "B3_news.csv"), "a", newline="", encoding="utf-8")
w = csv.writer(out)
for q in sys.argv[1:]:
    for eng, url in [("bing", f"https://www.bing.com/news/search?q={quote_plus(q)}&format=rss&count=50"),
                     ("google", f"https://news.google.com/rss/search?q={quote_plus(q)}&hl=en-US&gl=US&ceid=US:en")]:
        try:
            r = requests.get(url, headers=UA, timeout=40)
            root = ET.fromstring(r.content)
        except Exception as e:
            print("ERR", eng, q, e); continue
        items = root.findall(".//item")
        print(f"== {eng} '{q}': {len(items)}")
        for it in items:
            t = it.findtext("title") or ""; l = it.findtext("link") or ""; d = it.findtext("pubDate") or ""
            src = it.findtext("source") or ""
            if eng == "bing" and "apiclick" in l:
                l = parse_qs(urlparse(l).query).get("url", [l])[0]
            desc = re.sub("<[^>]+>", "", html.unescape(it.findtext("description") or ""))[:300]
            print(d[:16], "|", src[:25], "|", t[:140], "|", l[:200])
            w.writerow([q, eng, d, src, t, l, desc])
        time.sleep(1.5)
out.close()
