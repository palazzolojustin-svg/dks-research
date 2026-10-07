"""X03: Common Crawl census of dicks.com URLs per crawl (monthly-ish), saved as JSONL per collection.

For each Common Crawl collection from START onward, pulls the full index for a URL prefix
(default www.dickssportinggoods.com/f/* and /p/*), all pages, and writes
raw/X03_cc/<collection>_<tag>.jsonl (status, timestamp, url, filename, offset, length).
Usage: python X03_cc_census.py [prefix] [tag] [start_collection]
  python X03_cc_census.py "www.dickssportinggoods.com/f/*" f CC-MAIN-2023-06
  python X03_cc_census.py "www.dickssportinggoods.com/p/*" p CC-MAIN-2023-06
Weekly/monthly rerun: only new collections are fetched (existing files are skipped).
"""
import sys, os, json, time, requests

UA = {"User-Agent": "Mozilla/5.0 (research; DKS study)"}
OUT = os.path.join(os.path.dirname(__file__), "..", "raw", "X03_cc")
os.makedirs(OUT, exist_ok=True)


def get(url, params):
    for a in range(6):
        try:
            r = requests.get(url, params=params, headers=UA, timeout=240)
            if r.status_code in (200, 404):
                return r
            print("  http", r.status_code, flush=True)
        except Exception as e:
            print("  err", e, flush=True)
        time.sleep(15 * (a + 1))
    return None


def main(prefix, tag, start):
    colls = [c["id"] for c in requests.get("https://index.commoncrawl.org/collinfo.json", timeout=60).json()]
    colls = sorted([c for c in colls if c >= start])
    for c in colls:
        fn = os.path.join(OUT, f"{c}_{tag}.jsonl")
        if os.path.exists(fn):
            continue
        base = f"https://index.commoncrawl.org/{c}-index"
        r = get(base, {"url": prefix, "showNumPages": "true", "output": "json"})
        if r is None or r.status_code != 200:
            print(c, "no pages", flush=True)
            continue
        try:
            n = json.loads(r.text)["pages"]
        except Exception:
            n = 1
        rows = []
        ok = True
        for p in range(n):
            r = get(base, {"url": prefix, "output": "json", "page": p, "fl": "status,timestamp,url,filename,offset,length,mime"})
            if r is None:
                ok = False
                break
            if r.status_code == 404:
                break
            rows.extend(l for l in r.text.splitlines() if l.strip())
            time.sleep(1)
        if ok:
            open(fn, "w", encoding="utf-8").write("\n".join(rows) + "\n")
        print(c, "pages", n, "rows", len(rows), "OK" if ok else "FAIL", flush=True)


if __name__ == "__main__":
    a = sys.argv
    main(a[1] if len(a) > 1 else "www.dickssportinggoods.com/f/*", a[2] if len(a) > 2 else "f", a[3] if len(a) > 3 else "CC-MAIN-2023-06")
