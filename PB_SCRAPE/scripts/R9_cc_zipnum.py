"""R9: Common Crawl CDX lookup WITHOUT the index server (index.commoncrawl.org), using the public
ZipNum index files on data.commoncrawl.org:  cc-index/collections/<crawl>/indexes/cluster.idx + cdx-NNNNN.gz.
Binary-searches cluster.idx with HTTP Range requests (~30 small GETs), then range-fetches only the
compressed CDX blocks that cover the SURT prefix. Use when the index server is down / rate-limiting.

Rerun:  python R9_cc_zipnum.py <crawl> <surt_prefix> <out_tag>
  e.g.  python R9_cc_zipnum.py CC-MAIN-2026-39 "com,golfgalaxy)/f/" gg_f
Output: raw/R9/idx/<crawl>_<out_tag>.jsonl  (same fields as the CDX API: url, status, timestamp,
        filename, offset, length, mime ...)
"""
import gzip, io, json, os, sys, time
import requests
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from R9_cc_common import RAW, UA, _throttle

BASE = "https://data.commoncrawl.org/cc-index/collections/{c}/indexes/"
S = requests.Session()


def rng(url, a, b, tries=6):
    for i in range(tries):
        _throttle()
        try:
            r = S.get(url, headers={**UA, "Range": f"bytes={a}-{b}"}, timeout=120)
            if r.status_code in (200, 206):
                return r.content
            time.sleep(20 * (i + 1))
        except Exception:
            time.sleep(5 * (i + 1))
    raise RuntimeError(f"range fetch failed {url} {a}-{b}")


def size(url):
    r = S.head(url, headers=UA, timeout=60)
    return int(r.headers["Content-Length"])


def line_at(url, off, total):
    """First complete line starting after byte off (or at 0)."""
    chunk = rng(url, off, min(total - 1, off + 8191)).decode("utf-8", "replace")
    if off > 0:
        i = chunk.find("\n")
        chunk = chunk[i + 1:]
    j = chunk.find("\n")
    return chunk[:j] if j >= 0 else chunk


def lookup(crawl, prefix):
    url = BASE.format(c=crawl) + "cluster.idx"
    total = size(url)
    lo, hi = 0, total
    while hi - lo > 16384:  # find a position whose line key < prefix
        mid = (lo + hi) // 2
        key = line_at(url, mid, total).split(" ")[0]
        if key < prefix:
            lo = mid
        else:
            hi = mid
    # read forward from lo until keys pass the prefix range
    blocks, off, started = [], lo, False
    end_key = prefix[:-1] + chr(ord(prefix[-1]) + 1)
    prev = None
    while off < total:
        chunk = rng(url, off, min(total - 1, off + 262143)).decode("utf-8", "replace")
        lines = chunk.split("\n")
        if off > 0:
            lines = lines[1:]
        off += 262144
        done = False
        for l in lines[:-1]:
            parts = l.split("\t")
            if len(parts) < 4:
                continue
            key = parts[0].split(" ")[0]
            if key < prefix:
                prev = parts
                continue
            if prev is not None and not started:
                blocks.append(prev)  # block that starts before prefix may contain it
            started = True
            if key >= end_key:
                done = True
                break
            blocks.append(parts)
        if done:
            break
    if not started and prev is not None:
        blocks.append(prev)
    rows = []
    for p in blocks:
        fn, o, ln = p[1], int(p[2]), int(p[3])
        raw = rng(BASE.format(c=crawl) + fn, o, o + ln - 1)
        txt = gzip.GzipFile(fileobj=io.BytesIO(raw)).read().decode("utf-8", "replace")
        for l in txt.splitlines():
            if l.startswith(prefix):
                k, ts, js = l.split(" ", 2)
                d = json.loads(js, strict=False)
                d["timestamp"] = ts
                rows.append(d)
    return rows


def main():
    crawl, prefix, tag = sys.argv[1], sys.argv[2], sys.argv[3]
    out = os.path.join(RAW, "R9", "idx", f"{crawl}_{tag}.jsonl")
    if os.path.exists(out):
        print(crawl, tag, "exists"); return
    rows = lookup(crawl, prefix)
    with open(out, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    st = {}
    for r in rows:
        st[r.get("status")] = st.get(r.get("status"), 0) + 1
    print(crawl, tag, len(rows), st, flush=True)


if __name__ == "__main__":
    main()
