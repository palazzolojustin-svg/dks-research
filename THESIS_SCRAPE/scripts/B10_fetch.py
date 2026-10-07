"""B10: fetch NEW (accession not seen by H04/B8/B9) CMBS-type docs listed in raw/B10_fts_hits.csv into raw/B10_cache.
Keeps forms FWP / 424B* / 424H*; skips filers that are not CMBS depositors/trusts unless a sales-type query hit.
Rerun: python B10_fetch.py [hits_csv] [maxdocs]
"""
import csv, html, os, re, sys, time, requests
RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw"
C3 = os.path.join(RAW, "B10_cache"); os.makedirs(C3, exist_ok=True)
H = {"User-Agent": "IndependentResearch research-script palazzolojustin@gmail.com"}
HF = sys.argv[1] if len(sys.argv) > 1 else "B10_fts_hits.csv"
mx = int(sys.argv[2]) if len(sys.argv) > 2 else 10 ** 6
rows = [r for r in csv.DictReader(open(os.path.join(RAW, HF), encoding="utf-8")) if r["new"] == "True"]
FORMOK = re.compile(r"^(FWP|424B\d|424H)")
CMBS = re.compile(r"(Trust 20|Commercial Mortgage|Mortgage Securities|Mortgage Trust|Capital I|Mortgage Capital|BANK|Benchmark|CSAIL|COMM 20|GS Mortgage|Citigroup|Wells Fargo Comm|BBCMS|Barclays Comm|Deutsche Mortgage|JPMBB|JPMCC|JPMDB|UBS Comm|MSBAM|Morgan Stanley|3650|BMO 20|Credit Suisse|DBJPM|CD 20|Cantor|CFCRE|SG Comm|WFCM|DBUBS|Bank of America|Banc of America|Goldman)", re.I)
keep = [r for r in rows if FORMOK.match(r["form"]) and not r["url"].lower().endswith((".pdf", ".xml", ".zip", ".jpg", ".gif"))]
print("new rows", len(rows), "keep", len(keep), "cmbs-like", sum(bool(CMBS.search(r["filer"])) for r in keep), flush=True)
keep.sort(key=lambda r: (not CMBS.search(r["filer"]), r["file_date"]), reverse=False)
n = 0
for r in keep:
    if n >= mx: break
    u = r["url"]
    p = os.path.join(C3, re.sub(r"[^A-Za-z0-9_.-]", "_", u.split("/data/")[1]) + ".txt")
    if os.path.exists(p): continue
    time.sleep(0.15)
    try:
        resp = requests.get(u, headers=H, timeout=180)
    except Exception as ex:
        print("ERR", u, ex, flush=True); continue
    if resp.status_code != 200:
        print("HTTP", resp.status_code, u, flush=True); continue
    raw = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", resp.text)
    raw = re.sub(r"(?s)<[^>]+>", " ", raw)
    txt = re.sub(r"\s+", " ", html.unescape(raw))
    open(p, "w", encoding="utf-8").write(txt); n += 1
    print("fetched", r["file_date"], r["form"], r["filer"][:45], len(txt), flush=True)
print("DONE fetched", n)
