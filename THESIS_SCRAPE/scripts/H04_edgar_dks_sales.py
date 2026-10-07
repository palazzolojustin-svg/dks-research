"""H04: EDGAR FTS (CMBS term sheets / prospectuses) -> DICK'S store-level sales & occupancy-cost snippets.

Rerun: python H04_edgar_dks_sales.py TAG "phrase1&&phrase2" ["phrase3&&phrase4" ...]
 - lists hits (2023-01-01..2026-10-07), dedupes, fetches docs to raw/H04_edgar_cache (fast regex tag strip),
 - writes raw/H04_dkssales_<TAG>_snips.txt with windows around DICK'S mentions that contain sales/occupancy-cost numbers,
 - writes raw/H04_dkssales_<TAG>_hits.csv
"""
import csv
import html
import os
import re
import sys
import time
import requests

RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw"
CACHE = os.path.join(RAW, "H04_edgar_cache")
os.makedirs(CACHE, exist_ok=True)
H = {"User-Agent": "IndependentResearch research-script contact@example.org"}
tag = sys.argv[1]
queries = sys.argv[2:]


def fts(qq):
    out, frm = [], 0
    while True:
        r = requests.get("https://efts.sec.gov/LATEST/search-index",
                         params={"q": qq, "dateRange": "custom", "startdt": "2023-01-01", "enddt": "2026-10-07", "from": frm},
                         headers=H, timeout=60)
        d = r.json()
        if "hits" not in d:
            break
        hh = d["hits"]["hits"]
        if not hh:
            break
        out += hh
        frm += len(hh)
        if frm >= d["hits"]["total"]["value"]:
            break
        time.sleep(0.4)
    return out


hits = {}
for q in queries:
    qq = " ".join(f'"{p.strip()}"' for p in q.split("&&"))
    for x in fts(qq):
        s = x["_source"]
        adsh, fn = x["_id"].split(":", 1)
        if re.search(r"DICK'S SPORTING|FOOT LOCKER", " ".join(s.get("display_names", [])), re.I):
            continue
        if fn.lower().endswith(".pdf"):
            continue
        cik = s["ciks"][0].lstrip("0")
        url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{adsh.replace('-', '')}/{fn}"
        hits[url] = (s.get("file_date"), s.get("form"), (s.get("display_names") or [""])[0])
print("unique docs", len(hits), flush=True)
with open(os.path.join(RAW, f"H04_dkssales_{tag}_hits.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["file_date", "form", "filer", "url"])
    for u, (d, fm, fl) in sorted(hits.items(), key=lambda z: z[1][0]):
        w.writerow([d, fm, fl, u])

WIN = re.compile(r"Dick", re.I)
NEED = re.compile(r"(sales|occupancy cost|PSF|per square foot)", re.I)
NUM = re.compile(r"\$\s?\d")
out = open(os.path.join(RAW, f"H04_dkssales_{tag}_snips.txt"), "w", encoding="utf-8")
seen = set()
order = sorted(hits.items(), key=lambda z: z[1][0], reverse=bool(os.environ.get("H04_REVERSE")))
for u, (d, fm, fl) in order:
    cp =os.path.join(CACHE, re.sub(r"[^A-Za-z0-9_.-]", "_", u.split("/data/")[1]) + ".txt")
    if os.path.exists(cp):
        txt = open(cp, encoding="utf-8").read()
    else:
        time.sleep(0.25)
        try:
            r = requests.get(u, headers=H, timeout=180)
        except Exception as e:
            print("ERR", u, type(e).__name__, flush=True)
            continue
        raw = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", r.text)
        raw = re.sub(r"(?s)<[^>]+>", " ", raw)
        txt = re.sub(r"\s+", " ", html.unescape(raw))
        open(cp, "w", encoding="utf-8").write(txt)
    n = 0
    for m in WIN.finditer(txt):
        a, b = max(0, m.start() - 300), min(len(txt), m.end() + 600)
        snip = txt[a:b]
        if not (NEED.search(snip) and NUM.search(snip)):
            continue
        key = re.sub(r"\W", "", txt[m.start():m.start() + 250])
        if key in seen:
            continue
        seen.add(key)
        n += 1
        out.write(f"\n#### {d} | {fm} | {fl[:60]} | {u}\n... {snip} ...\n")
    print(d, fm, fl[:50], len(txt), "snips", n, flush=True)
out.close()
