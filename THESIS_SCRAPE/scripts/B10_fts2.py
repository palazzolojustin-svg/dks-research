"""B10 pass 2: broad FTS for CMBS prospectus forms with any DKS-name variant + "sales".
Key discovery: EDGAR FTS does NOT match curly-apostrophe "Dick’s" with the query "Dick's" (0 hits); docs with curly
apostrophes are reachable via the phrase "Dick s" (134 hits with "occupancy cost") or "Dicks".
Rerun: python B10_fts2.py -> raw/B10_fts2_hits.csv (new flag vs H04/B8/B9/B10-pass-1 accessions), then python B10_fetch.py B10_fts2_hits.csv
"""
import csv, os, re, time, glob, requests
RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw"
H = {"User-Agent": "IndependentResearch research-script palazzolojustin@gmail.com"}
known = set()
for fp in glob.glob(os.path.join(RAW, "*.csv")) + glob.glob(os.path.join(RAW, "*.txt")):
    b = os.path.basename(fp)
    if b.startswith("B10"): continue
    known |= set(re.findall(r"/data/\d+/(\d{18})/", open(fp, encoding="utf-8", errors="ignore").read()))
for d in ["H04_edgar_cache", "B8_cache", "B9_edgar_cache"]:
    for fn in os.listdir(os.path.join(RAW, d)):
        m = re.match(r"\d+_(\d{18})_", fn)
        if m: known.add(m.group(1))
print("known", len(known), flush=True)
QS = ['"Dick\'s" "sales"', '"Dick s" "sales"', '"Dicks" "sales"', '"Golf Galaxy" "sales"', '"House of Sport" "sales"',
      '"DSG" "occupancy cost"', '"Dick s" "occupancy cost"', '"Dick\'s" "Sq. Ft."', '"Dick s" "Sq. Ft."', '"Field House" "Dick s"',
      '"Dick\'s" "Field House"', '"Public Lands" "occupancy cost"', '"Field & Stream" "occupancy cost"']
FORMS = "FWP,424B2,424H,424B5,424B3"
YEARS = [(f"{y}-01-01", f"{y}-06-30") for y in range(2019, 2027)] + [(f"{y}-07-01", f"{y}-12-31") for y in range(2019, 2026)]


def fts(q, s, e):
    out, frm = [], 0
    while True:
        d = {}
        for k in range(7):
            try:
                r = requests.get("https://efts.sec.gov/LATEST/search-index",
                                 params={"q": q, "dateRange": "custom", "startdt": s, "enddt": e, "forms": FORMS, "from": frm}, headers=H, timeout=60)
                d = r.json()
                if "hits" in d: break
            except Exception:
                pass
            time.sleep(3 * (k + 1))
        hh = d.get("hits", {}).get("hits", [])
        if not hh: break
        out += hh; frm += len(hh)
        if frm >= d["hits"]["total"]["value"]: break
        time.sleep(0.3)
    return out


hits = {}
for q in QS:
    for s, e in YEARS:
        for x in fts(q, s, e):
            src = x["_source"]; adsh, fn = x["_id"].split(":", 1)
            cik = src["ciks"][0].lstrip("0")
            url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{adsh.replace('-', '')}/{fn}"
            if url not in hits:
                hits[url] = [src.get("file_date"), src.get("form"), (src.get("display_names") or [""])[0], q, adsh.replace("-", "")]
    print(q, "docs", len(hits), "new", sum(1 for v in hits.values() if v[4] not in known), flush=True)
with open(os.path.join(RAW, "B10_fts2_hits.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["file_date", "form", "filer", "url", "first_query", "acc", "new"])
    for u, v in sorted(hits.items(), key=lambda z: z[1][0]):
        w.writerow(v[:3] + [u] + v[3:] + [v[4] not in known])
print("DONE", len(hits))
