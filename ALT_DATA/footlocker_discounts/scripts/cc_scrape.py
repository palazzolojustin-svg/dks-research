"""Common Crawl scraper for archived Foot Locker NA/EMEA listing pages.

Steps (each resumable; outputs under ../data):
  index  : per crawl, stream cluster.idx, pull the CDX blocks covering Foot Locker hosts,
           keep status-200 HTML captures -> data/cdx/<crawl>.jsonl
  fetch  : choose listing pages per region-month (cap), range-fetch WARC records, parse
           product prices -> data/pages/cc_<crawl>.jsonl (one line per page)
Usage: python cc_scrape.py index|fetch [--crawls C1,C2] [--cap-na 2500] [--workers 12]
"""
import argparse
import gzip
import io
import json
import os
import random
import sys
import threading
import time
import zlib
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from flparse import DOMAINS, page_type, parse_products, region_of  # noqa: E402

BASE = "https://data.commoncrawl.org/"
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "data"))
LIVE = os.path.normpath(os.path.join(HERE, "..", "live"))  # gitignored work dir; sync.sh snapshots to data/
CRAWLS = [
    "CC-MAIN-2024-38", "CC-MAIN-2024-42", "CC-MAIN-2024-46", "CC-MAIN-2024-51",
    "CC-MAIN-2025-05", "CC-MAIN-2025-08", "CC-MAIN-2025-13", "CC-MAIN-2025-18",
    "CC-MAIN-2025-21", "CC-MAIN-2025-26", "CC-MAIN-2025-30", "CC-MAIN-2025-33",
    "CC-MAIN-2025-38", "CC-MAIN-2025-43", "CC-MAIN-2025-47", "CC-MAIN-2025-51",
    "CC-MAIN-2026-04", "CC-MAIN-2026-08", "CC-MAIN-2026-12", "CC-MAIN-2026-17",
    "CC-MAIN-2026-21", "CC-MAIN-2026-25", "CC-MAIN-2026-30", "CC-MAIN-2026-34",
    "CC-MAIN-2026-39",
]
PREFIXES = sorted(s + ")" for s in DOMAINS)  # SURT keys look like "com,footlocker)/path"
_local = threading.local()


def sess():
    if not hasattr(_local, "s"):
        _local.s = requests.Session()
    return _local.s


def get(url, rng=None, tries=12, timeout=120):
    h = {"Range": "bytes=%d-%d" % rng} if rng else {}
    for i in range(tries):
        try:
            r = sess().get(url, headers=h, timeout=timeout)
            if r.status_code in (200, 206):
                return r.content
            if r.status_code == 404:
                return None
        except requests.RequestException:
            pass
        # CC 503 SlowDown is intermittent: short jittered waits beat long exponential ones
        time.sleep(2 + random.random() * 4 + (10 if i >= 8 else 0))
    return None


def blocks_for(crawl):
    """Return list of (cdxfile, offset, length) blocks that may hold Foot Locker keys."""
    url = BASE + "cc-index/collections/%s/indexes/cluster.idx" % crawl
    blocks, prev = [], None
    pi = 0
    for attempt in range(4):
        try:
            with sess().get(url, stream=True, timeout=300) as r:
                if r.status_code != 200:
                    raise requests.RequestException(r.status_code)
                for raw in r.iter_lines():
                    line = raw.decode("utf-8", "replace")
                    key = line.split(" ", 1)[0]
                    # advance prefix pointer past prefixes that sort before this key and aren't matched
                    hit = any(key.startswith(p) for p in PREFIXES)
                    if hit:
                        if prev is not None and not any(prev[0].startswith(p) for p in PREFIXES):
                            blocks.append(prev[1])  # block just before first hit may hold keys
                        blocks.append(line.split("\t")[1:4])
                    else:
                        # a prefix may fall entirely inside the previous block
                        if prev is not None:
                            for p in PREFIXES:
                                if prev[0] < p < key:
                                    blocks.append(prev[1])
                                    break
                    prev = (key, line.split("\t")[1:4])
            break
        except requests.RequestException as e:
            print("cluster.idx retry", crawl, e, flush=True)
            time.sleep(10 * (attempt + 1))
    uniq, seen = [], set()
    for b in blocks:
        t = tuple(b)
        if t not in seen:
            seen.add(t)
            uniq.append((t[0], int(t[1]), int(t[2])))
    return uniq


def do_index(crawl):
    out = os.path.join(DATA, "cdx", crawl + ".jsonl")
    if os.path.exists(out):
        print("index exists", crawl, flush=True)
        return
    blocks = blocks_for(crawl)
    print(crawl, "blocks", len(blocks), flush=True)
    rows = []
    for f, off, ln in blocks:
        raw = get(BASE + "cc-index/collections/%s/indexes/%s" % (crawl, f), (off, off + ln - 1))
        if raw is None:
            print("  block fail", f, off, flush=True)
            continue
        for line in zlib.decompress(raw, 16 + zlib.MAX_WBITS).decode("utf-8", "replace").splitlines():
            key = line.split(" ", 1)[0]
            if not any(key.startswith(p) for p in PREFIXES):
                continue
            try:
                j = json.loads(line.split(" ", 2)[2])
            except Exception:
                continue
            if j.get("status") != "200" or "html" not in j.get("mime", ""):
                continue
            reg, cty = region_of(j["url"])
            if not reg:
                continue
            rows.append({"url": j["url"], "ts": line.split(" ")[1], "region": reg, "country": cty,
                         "ptype": page_type(j["url"]), "filename": j["filename"],
                         "offset": int(j["offset"]), "length": int(j["length"])})
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out + ".tmp", "w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    os.replace(out + ".tmp", out)
    from collections import Counter
    c = Counter((r["region"], r["ptype"]) for r in rows)
    print(crawl, "captures", len(rows), dict(c), flush=True)


def fetch_one(r):
    raw = get(BASE + r["filename"], (r["offset"], r["offset"] + r["length"] - 1))
    if raw is None:
        return dict(r, ok=False, err="fetch")
    try:
        txt = gzip.GzipFile(fileobj=io.BytesIO(raw)).read().decode("utf-8", "replace")
    except Exception:
        return dict(r, ok=False, err="gunzip")
    fmt, prods = parse_products(txt)
    out = {k: r[k] for k in ("url", "ts", "region", "country", "ptype")}
    out.update(src="cc", ok=True, fmt=fmt, n=len(prods), products=prods)
    return out


def do_fetch(crawl, caps, workers):
    idx = os.path.join(DATA, "cdx", crawl + ".jsonl")
    if not os.path.exists(idx):
        do_index(crawl)
    rows = [json.loads(l) for l in open(idx)]
    out = os.path.join(LIVE, "pages", "cc_%s.jsonl" % crawl)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    done = set()
    if os.path.exists(out):
        for l in open(out):
            try:
                j = json.loads(l)
                done.add((j["url"], j["ts"]))
            except Exception:
                pass
    # listing pages, one capture per URL per month; cap per region-month (random sample, fixed seed)
    by = {}
    for r in rows:
        if r["ptype"] != "listing":
            continue
        m = r["ts"][:6]
        by.setdefault((r["region"], m), {}).setdefault(r["url"], r)
    todo = []
    for (reg, m), d in sorted(by.items()):
        lst = sorted(d.values(), key=lambda x: x["url"])
        random.Random(zlib.crc32(('%s|%s|%s' % (crawl, reg, m)).encode())).shuffle(lst)  # stable across runs
        cap = caps.get(reg)
        todo += [r for r in (lst[:cap] if cap else lst) if (r["url"], r["ts"]) not in done]
    print(crawl, "to fetch", len(todo), "already", len(done), flush=True)
    lock = threading.Lock()
    n = 0
    with open(out, "a") as fh, ThreadPoolExecutor(workers) as ex:
        for fut in as_completed([ex.submit(fetch_one, r) for r in todo]):
            res = fut.result()
            if not res.get("ok"):
                continue
            with lock:
                fh.write(json.dumps(res) + "\n")
                n += 1
                if n % 500 == 0:
                    fh.flush()
                    print("  ", crawl, n, "/", len(todo), flush=True)
    print(crawl, "fetched", n, flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["index", "fetch"])
    ap.add_argument("--crawls", default=",".join(CRAWLS))
    ap.add_argument("--cap-na", type=int, default=2500)
    ap.add_argument("--cap-emea", type=int, default=0)  # 0 = no cap
    ap.add_argument("--workers", type=int, default=12)
    a = ap.parse_args()
    caps = {"NA": a.cap_na or None, "EMEA": a.cap_emea or None}
    for c in a.crawls.split(","):
        t0 = time.time()
        if a.step == "index":
            do_index(c)
        else:
            do_fetch(c, caps, a.workers)
        print(c, "done in %.0fs" % (time.time() - t0), flush=True)
