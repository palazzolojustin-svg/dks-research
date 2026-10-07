"""P5: Google News + Bing News RSS search for peer ticket / AUR / pricing evidence 2025-2026.
Rerun: python THESIS_SCRAPE\\scripts\\P5_newsrss.py "query1" "query2" ...   (no args = built-in list)
Appends to raw\\P5_news_rss.jsonl (dedup by link); prints title | date | source | link.
"""
import json, os, sys, time, urllib.parse
import requests
from bs4 import BeautifulSoup

OUT = r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\P5_news_rss.jsonl"
UA = {"User-Agent": "Mozilla/5.0 (research script; palazzolojustin@gmail.com)"}

QUERIES = [
    '"Academy Sports" "average ticket" 2026', '"Academy Sports" Labor Day comp 2026',
    'Circana athletic footwear average selling price 2026', 'Circana sports equipment sales 2026',
    'Circana footwear "average price" 2026', 'Circana "athletic apparel" 2026',
    '"Matt Powell" prices sneakers 2026', 'Beige Book retail prices tariffs September 2026',
    'Nike first quarter fiscal 2027 results pricing', 'Nike "full-price" ASP fiscal 2027',
    'Hoka price increase 2026', '"On Holding" price increase 2026', 'Deckers Hoka "average selling price" 2026',
    '"Under Armour" "average selling price" 2026', 'Columbia Sportswear pricing tariffs 2026',
    'VF "The North Face" price increase 2026', 'Amer Sports pricing 2026 Salomon Wilson',
    'JD Sports North America like-for-like 2026', '"Foot Locker" "average ticket" 2025',
    'Target "sporting goods" 2026 comparable', 'Walmart "average ticket" second quarter 2026',
    '"sporting goods" prices tariffs consumers 2026', 'sneaker prices rising 2026 tariffs',
    'Scheels sales 2026', '"Big 5 Sporting Goods" 2026', 'Hibbett 2026 sales',
    '"average unit retail" footwear 2026', '"units" "average selling price" athletic footwear 2026',
    'Genesco Journeys "average selling price" 2026', '"Shoe Carnival" "average selling price" 2026',
]


def gnews(q):
    u = "https://news.google.com/rss/search?q=" + urllib.parse.quote(q) + "&hl=en-US&gl=US&ceid=US:en"
    r = requests.get(u, headers=UA, timeout=30)
    soup = BeautifulSoup(r.content, "xml")
    for it in soup.find_all("item"):
        yield dict(engine="google", q=q, title=it.title.text if it.title else "", link=it.link.text if it.link else "",
                   date=it.pubDate.text if it.pubDate else "", source=it.source.text if it.source else "")


def bing(q):
    u = "https://www.bing.com/news/search?q=" + urllib.parse.quote(q) + "&format=rss"
    r = requests.get(u, headers=UA, timeout=30)
    soup = BeautifulSoup(r.content, "xml")
    for it in soup.find_all("item"):
        yield dict(engine="bing", q=q, title=it.title.text if it.title else "", link=it.link.text if it.link else "",
                   date=it.pubDate.text if it.pubDate else "", source="", desc=(it.description.text if it.description else "")[:400])


def main():
    qs = sys.argv[1:] or QUERIES
    seen = set()
    if os.path.exists(OUT):
        for l in open(OUT, encoding="utf-8"):
            seen.add(json.loads(l)["link"])
    fo = open(OUT, "a", encoding="utf-8")
    for q in qs:
        for fn in (gnews, bing):
            try:
                for d in fn(q):
                    if d["link"] in seen:
                        continue
                    seen.add(d["link"])
                    fo.write(json.dumps(d) + "\n")
                    print(f"[{d['engine'][0]}] {q[:40]} || {d['title'][:140]} | {d['date'][:16]} | {d['source']} | {d['link'][:160]}")
            except Exception as e:
                print("ERR", fn.__name__, q, e)
            time.sleep(0.8)


if __name__ == "__main__":
    main()
