"""R9 step 1: Common Crawl CDX census of a host/prefix across every crawl since a start collection.

Rerun:  python R9_cc_index.py <prefix> <tag> [start=CC-MAIN-2023-06]
  e.g.  python R9_cc_index.py www.golfgalaxy.com/f/ gg_f
        python R9_cc_index.py www.publiclands.com/f/ pl_f
        python R9_cc_index.py www.dickssportinggoods.com/f/ dks_f CC-MAIN-2026-39
Output: raw/R9/idx/<collection>_<tag>.jsonl (skips collections already saved; delete to refresh)
        and prints a status summary line per collection (n, n200, n403).
A new CC crawl lands roughly monthly (https://index.commoncrawl.org/collinfo.json).
"""
import collections, json, os, sys, requests
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from R9_cc_common import cc_index_prefix, RAW

OUT = os.path.join(RAW, "R9", "idx")
os.makedirs(OUT, exist_ok=True)


def main():
    prefix, tag = sys.argv[1], sys.argv[2]
    start = sys.argv[3] if len(sys.argv) > 3 else "CC-MAIN-2023-06"
    import time
    cache = os.path.join(OUT, "collinfo.json")
    info = None
    for i in range(3):
        try:
            info = requests.get("https://index.commoncrawl.org/collinfo.json", timeout=60).json()
            json.dump(info, open(cache, "w")); break
        except Exception as e:
            print("collinfo retry", i, e, file=sys.stderr); time.sleep(20 * (i + 1))
    if info is None:
        if os.path.exists(cache):
            info = json.load(open(cache))
        else:  # fallback: known 2022-2026 crawl ids
            ids = ("2022-05 2022-21 2022-27 2022-33 2022-40 2022-49 2023-06 2023-14 2023-23 2023-40 2023-50 2024-10 2024-18 "
                   "2024-22 2024-26 2024-30 2024-33 2024-38 2024-42 2024-46 2024-51 2025-05 2025-08 2025-13 2025-18 2025-21 "
                   "2025-26 2025-30 2025-33 2025-38 2025-43 2025-47 2025-51 2026-04 2026-08 2026-12 2026-17 2026-21 2026-25 "
                   "2026-30 2026-34 2026-39").split()
            info = [{"id": "CC-MAIN-" + x} for x in ids]
    colls = sorted(c["id"] for c in info if c["id"] >= start)
    for c in colls:
        fn = os.path.join(OUT, f"{c}_{tag}.jsonl")
        if os.path.exists(fn):
            rows = [json.loads(l, strict=False) for l in open(fn, encoding="utf-8") if l.startswith("{")]
        else:
            rows = cc_index_prefix(c, prefix)
            if rows is None:
                print(c, tag, "FAILED", flush=True); continue
            with open(fn, "w", encoding="utf-8") as f:
                for r in rows:
                    f.write(json.dumps(r) + "\n")
        st = collections.Counter(r.get("status") for r in rows)
        print(c, tag, "n", len(rows), "200", st.get("200", 0), "403", st.get("403", 0), flush=True)


if __name__ == "__main__":
    main()
