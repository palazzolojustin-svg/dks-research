"""WA5: news RSS sweep (Google News + Bing News RSS) for peer store-labor programs.
Rerun: python THESIS_SCRAPE/scripts/WA5_news_rss.py  -> raw/WA5_news_rss.json
"""
import requests, re, json, os, time, urllib.parse
from xml.etree import ElementTree as ET

UA = {"User-Agent": "Mozilla/5.0 (research; palazzolojustin@gmail.com)"}
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUERIES = [
    '"Academy Sports" payroll',
    '"Academy Sports" labor model',
    '"Academy Sports" "self-checkout"',
    '"Academy Sports" "expense discipline"',
    '"Academy Sports" SG&A leverage 2026',
    '"Academy Sports" store labor hours',
    '"Academy Sports" earnings call payroll',
    '"Academy Sports" "team members" layoffs',
    '"Academy Sports" Lawrence "labor"',
    '"Academy Sports" "base cost"',
]

def gnews(q):
    u = "https://news.google.com/rss/search?q=" + urllib.parse.quote(q) + "&hl=en-US&gl=US&ceid=US:en"
    return u

def bing(q):
    return "https://www.bing.com/news/search?q=" + urllib.parse.quote(q) + "&format=rss"

out = []
for q in QUERIES:
    for src, fn in (("google", gnews), ("bing", bing)):
        try:
            r = requests.get(fn(q), headers=UA, timeout=30)
            root = ET.fromstring(r.content)
            for it in root.iter("item"):
                out.append(dict(q=q, src=src, title=(it.findtext("title") or ""), link=(it.findtext("link") or ""),
                                date=(it.findtext("pubDate") or ""), desc=re.sub("<[^>]+>", " ", it.findtext("description") or "")[:400]))
        except Exception as e:
            out.append(dict(q=q, src=src, error=str(e)))
        time.sleep(0.6)
json.dump(out, open(os.path.join(BASE, "raw", "WA5_news_rss.json"), "w", encoding="utf-8"), indent=1)
seen = set()
for o in out:
    if "title" in o and o["title"] not in seen:
        seen.add(o["title"])
        print(o["src"], "|", o["date"][:16], "|", o["title"][:150], "|", o["link"][:120])
