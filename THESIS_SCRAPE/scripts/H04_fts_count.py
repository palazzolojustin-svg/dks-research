"""H04: quick EDGAR full-text-search hit counts / listing for phrases (no doc download).
Rerun: python H04_fts_count.py "phrase1" "phrase2" ...   (each arg is an exact phrase; combine with ' AND ' inside arg allowed)
"""
import sys
import time
import requests

H = {"User-Agent": "IndependentResearch research-script contact@example.org"}
for q in sys.argv[1:]:
    qq = " ".join(f'"{p.strip()}"' for p in q.split("&&"))
    r = requests.get("https://efts.sec.gov/LATEST/search-index",
                     params={"q": qq, "dateRange": "custom", "startdt": "2023-01-01", "enddt": "2026-10-07"},
                     headers=H, timeout=60)
    d = r.json()
    tot = d.get("hits", {}).get("total", {}).get("value")
    print("==", qq, "->", tot)
    for x in d.get("hits", {}).get("hits", [])[:15]:
        s = x["_source"]
        print("   ", s.get("file_date"), s.get("form"), s.get("display_names", [""])[0][:60], x["_id"])
    time.sleep(0.5)
