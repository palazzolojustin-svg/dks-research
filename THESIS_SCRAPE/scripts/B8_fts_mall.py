"""B8: EDGAR FTS for specific malls (earlier/later CMBS deals) to build multi-year pairs for single-point DKS stores.
Rerun: python B8_fts_mall.py "Westroads" "Crossgates Mall" ...  -> prints hits (date, form, url) not already cached; fetches them into raw/B8_cache.
"""
import sys, os, re, time, html, requests
RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw"
C1 = os.path.join(RAW, "H04_edgar_cache"); C2 = os.path.join(RAW, "B8_cache")
H = {"User-Agent": "IndependentResearch research-script palazzolojustin@gmail.com"}
def key(u): return re.sub(r"[^A-Za-z0-9_.-]", "_", u.split("/data/")[1]) + ".txt"
for mall in sys.argv[1:]:
    q = f'"{mall}" "Dick\'s"'
    r = requests.get("https://efts.sec.gov/LATEST/search-index", params={"q": q, "dateRange": "custom", "startdt": "2015-01-01", "enddt": "2026-10-07", "forms": "FWP,424B2,424H,424B5,424B3"}, headers=H, timeout=60).json()
    hh = r.get("hits", {}).get("hits", [])
    print("####", mall, r.get("hits", {}).get("total", {}).get("value"))
    seen_adsh = set()
    for x in hh:
        s = x["_source"]; adsh, fn = x["_id"].split(":", 1)
        if fn.lower().endswith(".pdf"): continue
        url = f"https://www.sec.gov/Archives/edgar/data/{s['ciks'][0].lstrip('0')}/{adsh.replace('-', '')}/{fn}"
        k = key(url); cached = os.path.exists(os.path.join(C1, k)) or os.path.exists(os.path.join(C2, k))
        print(" ", s.get("file_date"), s.get("form"), "CACHED" if cached else "NEW", url)
        if cached or adsh in seen_adsh: continue
        seen_adsh.add(adsh)
        time.sleep(0.3)
        try:
            t = requests.get(url, headers=H, timeout=180).text
        except Exception as e:
            print("ERR", e); continue
        t = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", t); t = re.sub(r"(?s)<[^>]+>", " ", t)
        open(os.path.join(C2, k), "w", encoding="utf-8").write(re.sub(r"\s+", " ", html.unescape(t)))
    time.sleep(0.5)
