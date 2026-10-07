"""H03: query Google News RSS (public feed) for a list of queries; dedupe; save CSV.
Rerun: python H03_newsrss.py queries.txt out.csv
"""
import sys, requests, csv, time, urllib.parse
import xml.etree.ElementTree as ET
qs = [l.strip() for l in open(sys.argv[1], encoding="utf-8") if l.strip()]
seen = set(); rows = []
for q in qs:
    u = "https://news.google.com/rss/search?q=" + urllib.parse.quote(q) + "&hl=en-US&gl=US&ceid=US:en"
    try:
        r = requests.get(u, timeout=60, headers={"User-Agent": "Mozilla/5.0"})
        root = ET.fromstring(r.content)
    except Exception as e:
        print("ERR", q, e); continue
    items = root.findall(".//item")
    print(f"### {q}: {len(items)}")
    for it in items:
        t = it.findtext("title"); l = it.findtext("link"); d = it.findtext("pubDate"); src = it.findtext("source")
        if t in seen: continue
        seen.add(t); rows.append([q, d, src, t, l])
        print(" -", d[5:16] if d else "", "|", src, "|", t[:150])
    time.sleep(1.5)
with open(sys.argv[2], "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["query", "date", "source", "title", "link"]); w.writerows(rows)
