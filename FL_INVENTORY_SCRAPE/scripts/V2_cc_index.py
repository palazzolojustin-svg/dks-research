"""X11 step 1: list every Common Crawl capture of dicks.com category pages (/f/...).

Rerun:  python X11_cc_index.py [collection ...]
  - With no args, uses every CC-MAIN collection from 2024 onward (collinfo.json).
  - Output: PB_SCRAPE/raw/X11_ccidx/<collection>.jsonl (one CDX JSON record per line).
  - Already-downloaded collections are skipped (delete the file to refresh).
The CC index server is flaky (502/504): the script retries with backoff.
New crawls appear roughly monthly at https://index.commoncrawl.org/collinfo.json, so a
human analyst can rerun this monthly, then run X11_cc_extract.py.
"""
import json, os, sys, time
import requests

OUT = os.path.join(os.path.dirname(__file__), "..", "raw", "V2", "ccidx")
os.makedirs(OUT, exist_ok=True)
HOSTS = ["www.dickssportinggoods.com/f/"]


def get(url, params, tries=8):
    for i in range(tries):
        try:
            r = requests.get(url, params=params, timeout=180)
            if r.status_code == 200:
                return r
            if r.status_code == 404:
                return None
            print("  status", r.status_code, "retry", i, flush=True)
        except Exception as e:
            print("  err", e, "retry", i, flush=True)
        time.sleep(10 + 10 * i)
    return None


def main():
    cols = sys.argv[1:]
    if not cols:
        info = requests.get("https://index.commoncrawl.org/collinfo.json", timeout=60).json()
        cols = [c["id"] for c in info if c["id"] >= "CC-MAIN-2024-10"]
    for cid in cols:
        fn = os.path.join(OUT, cid + ".jsonl")
        if os.path.exists(fn) and os.path.getsize(fn) > 0:
            print(cid, "exists, skip"); continue
        lines = []
        for host in HOSTS:
            r = get(f"https://index.commoncrawl.org/{cid}-index",
                    {"url": host, "matchType": "prefix", "showNumPages": "true"})
            pages = json.loads(r.text)["pages"] if r else 0
            for p in range(pages):
                r = get(f"https://index.commoncrawl.org/{cid}-index",
                        {"url": host, "matchType": "prefix", "output": "json", "page": p})
                if r:
                    lines += [l for l in r.text.splitlines() if l.startswith("{")]
        with open(fn, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(cid, len(lines), flush=True)


if __name__ == "__main__":
    main()
