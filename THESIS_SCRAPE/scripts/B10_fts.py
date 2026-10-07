"""B10: EDGAR full-text search extension for CMBS docs mentioning DICK'S / Golf Galaxy / HoS / FH with tenant sales.
Diffs against accessions already covered by H04 (raw/H04_edgar_cache, H04 snips/hit csvs) and B8/B9 (B8_hits*.csv, B8_cache, B9 csvs).
Rerun: python B10_fts.py  -> raw/B10_fts_hits.csv (all hits, with NEW flag) ; fetches NEW docs into raw/B10_cache/
"""
import csv, html, os, re, time, glob, requests
RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw"
C3 = os.path.join(RAW, "B10_cache"); os.makedirs(C3, exist_ok=True)
H = {"User-Agent": "IndependentResearch research-script palazzolojustin@gmail.com"}

known = set()
for fp in glob.glob(os.path.join(RAW, "*.csv")) + glob.glob(os.path.join(RAW, "*.txt")):
    if os.path.basename(fp).startswith("B10"): continue
    try:
        known |= set(re.findall(r"/data/\d+/(\d{18})/", open(fp, encoding="utf-8", errors="ignore").read()))
    except Exception:
        pass
for d in ["H04_edgar_cache", "B8_cache", "B9_edgar_cache"]:
    for fn in os.listdir(os.path.join(RAW, d)):
        m = re.match(r"\d+_(\d{18})_", fn)
        if m: known.add(m.group(1))
print("known accessions", len(known), flush=True)

A = ["Dick's Sporting Goods", "Dicks Sporting Goods", "DICK'S", "Golf Galaxy", "House of Sport", "Field House"]
S = ["occupancy cost", "sales PSF", "sales per square foot", "tenant sales", "reported sales", "Occ. Cost", "sales per SF", "trailing twelve", "Sales History"]
QS = []
for a in A:
    for s in S:
        if a in ("Field House",) and s not in ("sales PSF", "occupancy cost", "reported sales"):
            continue
        QS.append(f'"{a}" "{s}"')
FORMSETS = [None]  # no form filter: the EDGAR 'forms' param silently returns 0 when an unknown form (e.g. 424H/A) is listed; filter client-side
RANGES = [("2019-01-01", "2020-12-31"), ("2021-01-01", "2022-12-31"), ("2023-01-01", "2024-06-30"), ("2024-07-01", "2026-10-07")]


def fts(q, s, e, forms):
    out, frm = [], 0
    while True:
        d = {}
        for k in range(6):
            try:
                r = requests.get("https://efts.sec.gov/LATEST/search-index",
                                 params={"q": q, "dateRange": "custom", "startdt": s, "enddt": e, "forms": forms, "from": frm},
                                 headers=H, timeout=60)
                d = r.json()
                if "hits" in d: break
                print("  FTS no-hits resp", r.status_code, str(d)[:120], flush=True)
            except Exception as ex:
                print("  FTS exc", ex, flush=True)
            time.sleep(4 * (k + 1))
        hh = d.get("hits", {}).get("hits", [])
        if not hh: break
        out += hh; frm += len(hh)
        if frm >= d["hits"]["total"]["value"] or frm >= 2000: break
        time.sleep(0.4)
    return out


hits = {}
for q in QS:
    for forms in FORMSETS:
        for s, e in RANGES:
            for x in fts(q, s, e, forms):
                src = x["_source"]; adsh, fn = x["_id"].split(":", 1)
                if re.search(r"DICK'S SPORTING|FOOT LOCKER", " ".join(src.get("display_names", [])), re.I): continue
                cik = src["ciks"][0].lstrip("0")
                url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{adsh.replace('-', '')}/{fn}"
                if url not in hits:
                    hits[url] = [src.get("file_date"), src.get("form"), (src.get("display_names") or [""])[0], q, adsh.replace("-", "")]
    nn = sum(1 for v in hits.values() if v[4] not in known)
    print(q, "docs", len(hits), "new-acc docs", nn, flush=True)

with open(os.path.join(RAW, "B10_fts_hits.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["file_date", "form", "filer", "url", "first_query", "acc", "new"])
    for u, v in sorted(hits.items(), key=lambda z: z[1][0]):
        w.writerow(v[:3] + [u] + v[3:] + [v[4] not in known])


def key(u): return re.sub(r"[^A-Za-z0-9_.-]", "_", u.split("/data/")[1]) + ".txt"


new = 0
for u, v in sorted(hits.items(), key=lambda z: z[1][0], reverse=True):
    if v[4] in known or u.lower().endswith((".pdf", ".xml", ".zip")): continue
    p = os.path.join(C3, key(u))
    if os.path.exists(p): continue
    time.sleep(0.15)
    try:
        r = requests.get(u, headers=H, timeout=180)
    except Exception as ex:
        print("ERR", u, ex, flush=True); continue
    if r.status_code != 200:
        print("HTTP", r.status_code, u, flush=True); continue
    raw = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", r.text)
    raw = re.sub(r"(?s)<[^>]+>", " ", raw)
    txt = re.sub(r"\s+", " ", html.unescape(raw))
    open(p, "w", encoding="utf-8").write(txt); new += 1
    print("fetched", v[0], v[1], v[2][:40], len(txt), flush=True)
print("DONE fetched", new, "hits", len(hits))

