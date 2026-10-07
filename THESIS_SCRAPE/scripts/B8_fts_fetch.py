"""B8: EDGAR FTS -> CMBS docs mentioning DICK'S with tenant sales; fetch to cache (reuses H04 cache, new docs -> raw/B8_cache).
Rerun: python B8_fts_fetch.py [TAG "q1" "q2" ...]  (writes raw/B8_hits[TAG].csv; idempotent, skips cached docs)
"""
import csv, html, os, re, time, requests
RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw"
C1 = os.path.join(RAW, "H04_edgar_cache"); C2 = os.path.join(RAW, "B8_cache")
os.makedirs(C2, exist_ok=True)
H = {"User-Agent": "IndependentResearch research-script palazzolojustin@gmail.com"}
QS = ['"Dick\'s Sporting Goods" "occupancy cost"', '"Dick\'s" "occupancy cost"', '"Dick\'s" "sales PSF"',
      '"Dick\'s Sporting Goods" "sales per square foot"', '"Golf Galaxy" "occupancy cost"', '"House of Sport" "sales"',
      '"Dick\'s" "Field House"', '"Dick\'s" "TTM" "sales"', '"Dicks Sporting Goods" "occupancy cost"',
      '"Dick\'s" "tenant sales"', '"Golf Galaxy" "sales PSF"', '"Dick\'s" "Sales History"']
FORMS = "FWP,424B2,424H,424B5,424B3"
import sys
TAG = ""
if len(sys.argv) > 2:
    TAG = sys.argv[1]; QS = sys.argv[2:]
def fts(q, s, e):
    out, frm = [], 0
    while True:
        for k in range(4):
            try:
                r = requests.get("https://efts.sec.gov/LATEST/search-index", params={"q": q, "dateRange": "custom", "startdt": s, "enddt": e, "forms": FORMS, "from": frm}, headers=H, timeout=60)
                d = r.json(); break
            except Exception as ex:
                time.sleep(3); d = {}
        hh = d.get("hits", {}).get("hits", [])
        if not hh: break
        out += hh; frm += len(hh)
        if frm >= d["hits"]["total"]["value"]: break
        time.sleep(0.3)
    return out
hits = {}
for q in QS:
    for s, e in [("2019-01-01", "2022-12-31"), ("2023-01-01", "2026-10-07")]:
        for x in fts(q, s, e):
            src = x["_source"]; adsh, fn = x["_id"].split(":", 1)
            if fn.lower().endswith(".pdf"): continue
            if re.search(r"DICK'S SPORTING|FOOT LOCKER", " ".join(src.get("display_names", [])), re.I): continue
            cik = src["ciks"][0].lstrip("0")
            url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{adsh.replace('-', '')}/{fn}"
            if url not in hits:
                hits[url] = [src.get("file_date"), src.get("form"), (src.get("display_names") or [""])[0], q]
        print(q, s[:4], len(hits), flush=True)
with open(os.path.join(RAW, f"B8_hits{TAG}.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["file_date", "form", "filer", "url", "first_query"])
    for u, v in sorted(hits.items(), key=lambda z: z[1][0]): w.writerow([v[0], v[1], v[2], u, v[3]])
def key(u): return re.sub(r"[^A-Za-z0-9_.-]", "_", u.split("/data/")[1]) + ".txt"
new = 0
for u in sorted(hits, key=lambda z: hits[z][0], reverse=True):
    k = key(u)
    if os.path.exists(os.path.join(C1, k)) or os.path.exists(os.path.join(C2, k)): continue
    time.sleep(0.2)
    try:
        r = requests.get(u, headers=H, timeout=180)
    except Exception as ex:
        print("ERR", u, ex, flush=True); continue
    if r.status_code != 200: print("HTTP", r.status_code, u, flush=True); continue
    raw = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", r.text)
    raw = re.sub(r"(?s)<[^>]+>", " ", raw)
    txt = re.sub(r"\s+", " ", html.unescape(raw))
    open(os.path.join(C2, k), "w", encoding="utf-8").write(txt); new += 1
    print("fetched", hits[u][0], hits[u][2][:40], len(txt), flush=True)
print("DONE new", new, "total", len(hits))

