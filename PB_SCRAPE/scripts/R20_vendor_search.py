"""R20_vendor_search.py
Search alt-data vendors' PUBLIC outputs that mention DICK'S owned brands / private label.
Engines: Google News RSS, Bing News RSS, DuckDuckGo HTML, Bing web HTML (no keys, no login).
Rerun (e.g. weekly):  python R20_vendor_search.py [queries_file]
  queries_file = text file, one query per line (default: built-in list below).
Output: PB_SCRAPE/raw/R20_search_<date>.csv  (engine, query, title, url, date, snippet)
"""
import requests, sys, csv, os, time, html, re, urllib.parse
from email.utils import parsedate_to_datetime
from xml.etree import ElementTree as ET
from datetime import datetime
from bs4 import BeautifulSoup

H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36",
     "Accept-Language": "en-US,en;q=0.9"}
VENDORS = ["YipitData", "Earnest Analytics", "Consumer Edge", "Second Measure", "Numerator", "Circana", "Placer.ai",
           "M Science", "Edison Trends", "Facteus", "Cardify", "Rakuten Intelligence", "Similarweb", "Profitero",
           "DataWeave", "Stackline", "EDITED", "Trendalytics", "Klover", "Bloomberg Second Measure"]
DEFAULT_Q = []
for v in VENDORS:
    DEFAULT_Q += [f'"{v}" "Dick\'s Sporting Goods"', f'"{v}" CALIA OR VRST OR Maxfli', f'"{v}" "private label" "Dick\'s"']


def gnews(q):
    out = []
    r = requests.get("https://news.google.com/rss/search", params={"q": q, "hl": "en-US", "gl": "US", "ceid": "US:en"}, headers=H, timeout=30)
    root = ET.fromstring(r.content)
    for it in root.iter("item"):
        d = it.findtext("pubDate")
        try:
            d = parsedate_to_datetime(d).date().isoformat()
        except Exception:
            pass
        src = it.find("source")
        out.append(("gnews", html.unescape(it.findtext("title") or ""), it.findtext("link") or "", d,
                    (src.text if src is not None else "")))
    return out


def bingnews(q):
    out = []
    r = requests.get("https://www.bing.com/news/search", params={"q": q, "format": "rss", "count": "100"}, headers=H, timeout=30)
    root = ET.fromstring(r.content)
    for it in root.iter("item"):
        d = it.findtext("pubDate")
        try:
            d = parsedate_to_datetime(d).date().isoformat()
        except Exception:
            pass
        out.append(("bingnews", html.unescape(it.findtext("title") or ""), it.findtext("link") or "", d,
                    html.unescape(re.sub("<[^>]+>", "", it.findtext("description") or ""))[:300]))
    return out


def ddg(q):
    out = []
    r = requests.post("https://html.duckduckgo.com/html/", data={"q": q}, headers=H, timeout=30)
    s = BeautifulSoup(r.text, "html.parser")
    for a in s.select("a.result__a"):
        href = a.get("href", "")
        m = re.search(r"uddg=([^&]+)", href)
        if m:
            href = urllib.parse.unquote(m.group(1))
        snip = a.find_parent("div", class_="result")
        sn = snip.select_one(".result__snippet").get_text(" ", strip=True) if snip and snip.select_one(".result__snippet") else ""
        out.append(("ddg", a.get_text(" ", strip=True), href, "", sn[:300]))
    return out


def bingweb(q):
    out = []
    r = requests.get("https://www.bing.com/search", params={"q": q, "count": "30"}, headers=H, timeout=30)
    s = BeautifulSoup(r.text, "html.parser")
    for li in s.select("li.b_algo"):
        a = li.select_one("h2 a")
        if not a:
            continue
        p = li.select_one("p") or li.select_one(".b_caption")
        out.append(("bingweb", a.get_text(" ", strip=True), a.get("href", ""), "", (p.get_text(" ", strip=True) if p else "")[:300]))
    return out


ENGINES = {"gnews": gnews, "bingnews": bingnews, "ddg": ddg, "bingweb": bingweb}


def run(queries, engines=("gnews", "bingnews", "ddg", "bingweb"), sleep=1.2):
    rows = []
    for q in queries:
        for e in engines:
            try:
                res = ENGINES[e](q)
            except Exception as ex:
                print("ERR", e, q, ex)
                res = []
            for x in res:
                rows.append([x[0], q, x[1], x[2], x[3], x[4]])
            print(f"{e:9s} {len(res):3d}  {q}")
            time.sleep(sleep)
    return rows


if __name__ == "__main__":
    qs = DEFAULT_Q
    if len(sys.argv) > 1:
        qs = [l.strip() for l in open(sys.argv[1], encoding="utf-8") if l.strip()]
    tag = sys.argv[2] if len(sys.argv) > 2 else datetime.now().strftime("%Y%m%d_%H%M")
    rows = run(qs)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "raw", f"R20_search_{tag}.csv")
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["engine", "query", "title", "url", "date", "snippet"])
        w.writerows(rows)
    print(len(rows), "rows ->", out)
