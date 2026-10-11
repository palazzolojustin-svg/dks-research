"""Wayback Machine scraper for archived Foot Locker NA/EMEA listing pages.

Steps (resumable; outputs under ../data):
  cdx   : list status-200 HTML captures of listing pages per host, Sep 2024 - Oct 2026
          -> data/wb_cdx/<host>.jsonl
  fetch : one capture per URL per month, capped per region-month after counting pages already
          collected from Common Crawl; fetch raw HTML (id_ mode), parse prices
          -> data/pages/wb_<host>.jsonl (same schema as cc_*.jsonl, src="wb")
Usage: python wb_scrape.py cdx|fetch [--hosts h1,h2] [--target-na 2500] [--workers 4]
"""
import argparse
import glob
import json
import os
import random
import sys
import threading
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from flparse import DOMAINS, page_type, parse_products, region_of  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "data"))
CDX = "https://web.archive.org/cdx/search/cdx"
HOSTS = ["www." + ".".join(reversed(s.split(","))) for s in DOMAINS]
FROM, TO = "20240901", "20261031"
_local = threading.local()


def sess():
    if not hasattr(_local, "s"):
        s = requests.Session()
        s.headers["User-Agent"] = "research-archive-reader/1.0 (academic price study)"
        _local.s = s
    return _local.s


def get(url, params=None, tries=7, timeout=90):
    for i in range(tries):
        try:
            r = sess().get(url, params=params, timeout=timeout)
            if r.status_code == 200:
                return r
            if r.status_code in (404, 403):
                return None
            if r.status_code == 429:
                time.sleep(60 + 30 * i)
                continue
        except requests.RequestException:
            pass
        time.sleep(min(120, 3 * 2 ** i) + random.random())
    return None


def do_cdx(host):
    out = os.path.join(DATA, "wb_cdx", host + ".jsonl")
    if os.path.exists(out):
        print("cdx exists", host, flush=True)
        return
    rows, seen = [], set()
    base = dict(url=host + "/*", output="json", fl="timestamp,original,statuscode,mimetype",
                filter=["statuscode:200", "mimetype:text/html", "original:.*/(category|buy|search)[/?.].*"], **{"from": FROM, "to": TO})
    r = get(CDX, dict(base, showNumPages="true"))
    pages = int(r.text.strip()) if r is not None and r.text.strip().isdigit() else 1
    print(host, "cdx pages", pages, flush=True)
    for pg in range(pages):
        r = get(CDX, dict(base, page=pg), timeout=180)
        if r is None:
            print("  cdx page fail", host, pg, flush=True)
            continue
        try:
            data = r.json()
        except ValueError:
            continue
        for ts, orig, sc, mime in data[1:] if data and data[0][0] == "timestamp" else data:
            if page_type(orig) != "listing":
                continue
            reg, cty = region_of(orig)
            if not reg:
                continue
            k = (orig.split("#")[0], ts[:6])
            if k in seen:
                continue
            seen.add(k)
            rows.append({"url": orig, "ts": ts, "region": reg, "country": cty, "ptype": "listing"})
        time.sleep(1.5)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out + ".tmp", "w") as fh:
        for x in rows:
            fh.write(json.dumps(x) + "\n")
    os.replace(out + ".tmp", out)
    print(host, "listing url-months", len(rows), dict(Counter(x["ts"][:6] for x in rows)), flush=True)


def have_counts():
    """Pages already collected (cc_* and wb_*), by (region, yyyymm), counting pages with products."""
    c = Counter()
    for f in glob.glob(os.path.join(DATA, "pages", "*.jsonl")):
        for l in open(f):
            try:
                j = json.loads(l)
            except ValueError:
                continue
            if j.get("n", 0) > 0:
                c[(j["region"], j["ts"][:6])] += 1
    return c


def fetch_one(r):
    resp = get("https://web.archive.org/web/%sid_/%s" % (r["ts"], r["url"]))
    if resp is None:
        return dict(r, ok=False)
    fmt, prods = parse_products(resp.text)
    out = dict(r, src="wb", ok=True, fmt=fmt, n=len(prods), products=prods)
    return out


def do_fetch(hosts, target, workers):
    have = have_counts()
    todo = []
    for host in hosts:
        f = os.path.join(DATA, "wb_cdx", host + ".jsonl")
        if not os.path.exists(f):
            continue
        out = os.path.join(DATA, "pages", "wb_%s.jsonl" % host)
        done = set()
        if os.path.exists(out):
            done = {(j["url"], j["ts"]) for j in map(json.loads, open(out))}
        by = {}
        for x in map(json.loads, open(f)):
            by.setdefault((x["region"], x["ts"][:6]), []).append(x)
        for (reg, m), lst in sorted(by.items()):
            random.Random(hash((host, m)) & 0xFFFF).shuffle(lst)
            cap = target.get(reg)
            need = len(lst) if cap is None else max(0, cap - have[(reg, m)])
            todo += [(host, x) for x in lst[:need] if (x["url"], x["ts"]) not in done]
    print("wayback to fetch", len(todo), flush=True)
    random.shuffle(todo)  # spread load across hosts/months
    fhs, lock, n = {}, threading.Lock(), 0
    with ThreadPoolExecutor(workers) as ex:
        futs = {ex.submit(fetch_one, x): h for h, x in todo}
        for fut in as_completed(futs):
            res = fut.result()
            if not res.get("ok"):
                continue
            h = futs[fut]
            with lock:
                if h not in fhs:
                    fhs[h] = open(os.path.join(DATA, "pages", "wb_%s.jsonl" % h), "a")
                fhs[h].write(json.dumps(res) + "\n")
                n += 1
                if n % 200 == 0:
                    for fh in fhs.values():
                        fh.flush()
                    print("  fetched", n, "/", len(todo), flush=True)
    for fh in fhs.values():
        fh.close()
    print("wayback fetched", n, flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["cdx", "fetch"])
    ap.add_argument("--hosts", default=",".join(HOSTS))
    ap.add_argument("--target-na", type=int, default=2500)
    ap.add_argument("--target-emea", type=int, default=0)  # 0 = take everything
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    hosts = a.hosts.split(",")
    os.makedirs(os.path.join(DATA, "pages"), exist_ok=True)
    if a.step == "cdx":
        for h in hosts:
            do_cdx(h)
    else:
        do_fetch(hosts, {"NA": a.target_na or None, "EMEA": a.target_emea or None}, a.workers)
