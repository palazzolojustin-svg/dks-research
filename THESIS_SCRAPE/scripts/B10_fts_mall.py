"""B10: mall-specific EDGAR FTS (2015-2026, no form filter) for the stores B10 found, to find other-year DICK'S sales reads.
Rerun: python B10_fts_mall.py "Woodlands Mall" "Shoppes at Parma" ...  -> prints hits; fetches CMBS-form docs into raw/B10_cache;
prints DICK'S rows with $ figures near sales words.
"""
import html, os, re, sys, time, requests
RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw"
H = {"User-Agent": "IndependentResearch research-script palazzolojustin@gmail.com"}
CACHES = [os.path.join(RAW, d) for d in ["B10_cache", "B8_cache", "H04_edgar_cache"]]


def fts(q):
    out, frm = [], 0
    while True:
        d = {}
        for k in range(7):
            try:
                d = requests.get("https://efts.sec.gov/LATEST/search-index", params={"q": q, "dateRange": "custom", "startdt": "2015-01-01", "enddt": "2026-10-07", "from": frm}, headers=H, timeout=60).json()
                if "hits" in d: break
            except Exception:
                pass
            time.sleep(3 * (k + 1))
        hh = d.get("hits", {}).get("hits", [])
        if not hh: break
        out += hh; frm += len(hh)
        if frm >= d["hits"]["total"]["value"]: break
    return out


for mall in sys.argv[1:]:
    hits = {}
    for q in [f'"{mall}" "Dick\'s"', f'"{mall}" "Dick s"', f'"{mall}" "Dicks"']:
        for x in fts(q):
            s = x["_source"]; adsh, fn = x["_id"].split(":", 1)
            if not re.match(r"^(FWP|424B\d|424H)", s.get("form", "")): continue
            cik = s["ciks"][0].lstrip("0")
            hits[f"https://www.sec.gov/Archives/edgar/data/{cik}/{adsh.replace('-', '')}/{fn}"] = s.get("file_date")
    print("=====", mall, len(hits), "docs", sorted(set(hits.values())), flush=True)
    for u, dt in sorted(hits.items(), key=lambda z: z[1]):
        k = re.sub(r"[^A-Za-z0-9_.-]", "_", u.split("/data/")[1]) + ".txt"
        p = next((os.path.join(c, k) for c in CACHES if os.path.exists(os.path.join(c, k))), None)
        if not p:
            time.sleep(0.2)
            try:
                r = requests.get(u, headers=H, timeout=180)
            except Exception as ex:
                print("ERR", u, ex); continue
            raw = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", r.text)
            txt = re.sub(r"\s+", " ", html.unescape(re.sub(r"(?s)<[^>]+>", " ", raw)))
            p = os.path.join(CACHES[0], k); open(p, "w", encoding="utf-8").write(txt)
        t = open(p, encoding="utf-8", errors="ignore").read()
        seen = set()
        mpos = [m.start() for m in re.finditer(re.escape(mall), t)]
        for m in re.finditer(r"(Dick[’'`]?s\b|DICK[’']S)", t):
            if not any(0 <= m.start() - q <= 40000 for q in mpos): continue
            s = t[max(0, m.start() - 150): m.start() + 260]
            if re.search(r"sales|PSF|per square foot|Occupancy", s, re.I) and re.search(r"\$\s?\d", s[150:]):
                kk = re.sub(r"\W", "", s[150:260])
                if kk in seen: continue
                seen.add(kk)
                print(f"  [{dt}] {u.split('/')[-1]} :: {s}")
