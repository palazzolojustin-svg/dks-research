"""H03: Bing News RSS (public feed; returns publisher URLs). Rerun: python H03_bingnews.py queries.txt [max]
Also supports Google-News-style fallback via news.google.com RSS if Bing returns nothing.
"""
import sys, time, requests, urllib.parse
import xml.etree.ElementTree as ET
qs = [l.strip() for l in open(sys.argv[1], encoding="utf-8") if l.strip()]
mx = int(sys.argv[2]) if len(sys.argv) > 2 else 15
for q in qs:
    print("###", q)
    try:
        r = requests.get("https://www.bing.com/news/search?format=rss&q=" + urllib.parse.quote(q),
                         headers={"User-Agent": "Mozilla/5.0"}, timeout=60)
        items = ET.fromstring(r.content).findall(".//item")
    except Exception as e:
        print("ERR", e); items = []
    for it in items[:mx]:
        link = it.findtext("link") or ""
        if "url=" in link:
            link = urllib.parse.unquote(link.split("url=")[1].split("&")[0])
        print(" -", (it.findtext("pubDate") or "")[5:16], "|", (it.findtext("title") or "")[:110], "|", link)
    time.sleep(1.5)
