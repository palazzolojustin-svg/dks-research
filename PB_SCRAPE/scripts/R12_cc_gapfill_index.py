"""R12: fill gaps in the CC index for the 45 X02 census category slugs.
For each (crawl, slug) where X03_cc/R9 idx files have no HTTP-200 capture, query index.commoncrawl.org directly with
url=<host>/f/<slug>* (prefix), keep exact-slug rows, and append them to raw/R12_cc_idx_extra.jsonl (same schema as the
X03/R9 idx files). R12_cc_plp.py then picks them up (it also reads R12_cc_idx_extra.jsonl).
Rerun: python PB_SCRAPE\\scripts\\R12_cc_gapfill_index.py CC-MAIN-2025-33 CC-MAIN-2026-34 ...
"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from R9_cc_common import _get
from R12_common import RAW
from R12_wayback_plp import DKS, GG, HOSTS
from R12_cc_plp import candidates

OUT = os.path.join(RAW, "R12_cc_idx_extra.jsonl")


def main(crawls):
    have = {(c, h, s) for c, h, s, r in candidates([])}
    done = set()
    if os.path.exists(OUT):
        for l in open(OUT, encoding="utf-8"):
            try:
                j = json.loads(l)
                done.add((j["_crawl"], j["_host"], j["_slug"]))
            except Exception:
                pass
    if os.path.exists(OUT + ".tried"):
        done |= {tuple(l.strip().split("\t")) for l in open(OUT + ".tried", encoding="utf-8") if l.strip()}
    fh = open(OUT, "a", encoding="utf-8")
    tr = open(OUT + ".tried", "a", encoding="utf-8")
    for crawl in crawls:
        for host, slugs in (("dks", DKS), ("gg", GG)):
            for slug in slugs:
                k = (crawl, host, slug)
                if k in have or k in done:
                    continue
                r = _get(f"https://index.commoncrawl.org/{crawl}-index",
                         {"url": f"{HOSTS[host]}/f/{slug}", "matchType": "prefix", "output": "json",
                          "fl": "status,timestamp,url,filename,offset,length,mime"}, tries=4)
                n = 0
                if r is not None and r.status_code == 200:
                    for l in r.text.splitlines():
                        if not l.startswith("{"):
                            continue
                        j = json.loads(l, strict=False)
                        path = j["url"].split("://", 1)[-1].split("/", 1)[-1]
                        if path.split("?", 1)[0].rstrip("/") == f"f/{slug}":
                            j.update(_crawl=crawl, _host=host, _slug=slug)
                            fh.write(json.dumps(j) + "\n")
                            n += 1
                    fh.flush()
                tr.write("\t".join(k) + "\n")
                tr.flush()
                print(crawl, host, slug, "rows", n, "http", r.status_code if r is not None else None, flush=True)
                time.sleep(1.5)
    print("DONE", flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
