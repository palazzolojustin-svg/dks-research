"""P3: Google News / Bing News RSS search for tariff pass-through research (Fed, academic) and retail price evidence.
Rerun: python THESIS_SCRAPE\\scripts\\P3_newsrss.py "query one" "query two" ...  -> appends to raw\\P3_newsrss.txt
"""
import sys, requests, urllib.parse, xml.etree.ElementTree as ET

H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0 Safari/537.36"}
OUT = r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\P3_newsrss.txt"


def gnews(q):
    u = "https://news.google.com/rss/search?q=" + urllib.parse.quote(q) + "&hl=en-US&gl=US&ceid=US:en"
    r = requests.get(u, headers=H, timeout=40)
    root = ET.fromstring(r.content)
    return [(i.findtext("pubDate"), i.findtext("title"), i.findtext("link"), (i.findtext("source") or "")) for i in root.iter("item")]


def bing(q):
    u = "https://www.bing.com/news/search?q=" + urllib.parse.quote(q) + "&format=rss"
    r = requests.get(u, headers=H, timeout=40)
    try:
        root = ET.fromstring(r.content)
    except ET.ParseError:
        return []
    return [(i.findtext("pubDate"), i.findtext("title"), i.findtext("link"), "bing") for i in root.iter("item")]


if __name__ == "__main__":
    with open(OUT, "a", encoding="utf-8") as fo:
        for q in sys.argv[1:]:
            for name, fn in (("G", gnews), ("B", bing)):
                try:
                    items = fn(q)
                except Exception as e:
                    items = []
                    print(name, q, "ERR", e)
                fo.write(f"\n## [{name}] {q} ({len(items)})\n")
                print(f"\n## [{name}] {q} ({len(items)})")
                for d, t, l, s in items[:25]:
                    line = f"- {d} | {t} | {s} | {l}"
                    fo.write(line + "\n")
                    print(line[:260])
