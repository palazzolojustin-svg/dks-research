"""R9 shared helpers for Common Crawl (CC) work on dicks.com / golfgalaxy.com / publiclands.com.

Import from other R9 scripts:  from R9_cc_common import load_idx, fetch_warc, cc_index_prefix
- load_idx(path): read a CDX JSONL file (tolerant of bad lines; strict=False JSON).
- fetch_warc(rec): byte-range GET of one WARC record from data.commoncrawl.org, returns the
  decoded HTTP body (str) or None.
- cc_index_prefix(collection, prefix): full CDX listing (all index pages) for a URL prefix,
  with retries (CC index is flaky: 502/504).
No auth needed. CC is public (https://commoncrawl.org). Be polite: <= ~12 parallel range GETs.
"""
import gzip, io, json, os, sys, time
import requests

UA = {"User-Agent": "Mozilla/5.0 (research; DKS owned-brand study; R9)"}
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
RAW = os.path.join(ROOT, "raw")
S = requests.Session()


def load_idx(path):
    out = []
    if not os.path.exists(path):
        return out
    for l in open(path, encoding="utf-8", errors="replace"):
        l = l.strip()
        if not l.startswith("{"):
            continue
        try:
            out.append(json.loads(l, strict=False))
        except Exception:
            pass
    return out


import threading
_TL = threading.Lock()
_STATE = {"next": 0.0, "pause_until": 0.0, "pause": 60.0}
MIN_INTERVAL = float(os.environ.get("R9_CC_MIN_INTERVAL", "0.35"))  # seconds between requests per process


def _throttle():
    with _TL:
        now = time.time()
        wait = max(_STATE["next"], _STATE["pause_until"]) - now
        _STATE["next"] = max(now, _STATE["pause_until"]) + MIN_INTERVAL
    if wait > 0:
        time.sleep(wait)


def fetch_warc(rec, tries=6):
    """Polite fetch: global min interval; on CloudFront 403/503 (rate limit) pause ALL threads
    with exponential back-off (60s → 15 min). Never retries aggressively."""
    off, ln = int(rec["offset"]), int(rec["length"])
    for i in range(tries):
        _throttle()
        try:
            r = S.get("https://data.commoncrawl.org/" + rec["filename"],
                      headers={**UA, "Range": f"bytes={off}-{off + ln - 1}"}, timeout=120)
            if r.status_code in (200, 206):
                with _TL:
                    _STATE["pause"] = 60.0
                raw = gzip.GzipFile(fileobj=io.BytesIO(r.content)).read()
                parts = raw.split(b"\r\n\r\n", 2)
                body = parts[2] if len(parts) == 3 else raw
                return body.decode("utf-8", "replace")
            if r.status_code in (403, 429, 503):
                with _TL:
                    if time.time() >= _STATE["pause_until"]:
                        _STATE["pause_until"] = time.time() + _STATE["pause"]
                        print(f"  [cc] HTTP {r.status_code}: pausing {_STATE['pause']:.0f}s", file=sys.stderr, flush=True)
                        _STATE["pause"] = min(_STATE["pause"] * 2, 900.0)
                continue
        except Exception:
            time.sleep(3 * (i + 1))
    return None


def _get(url, params, tries=8):
    for i in range(tries):
        try:
            r = requests.get(url, params=params, headers=UA, timeout=240)
            if r.status_code in (200, 404):
                return r
            print("  http", r.status_code, "retry", i, file=sys.stderr, flush=True)
        except Exception as e:
            print("  err", e, "retry", i, file=sys.stderr, flush=True)
        time.sleep(10 + 10 * i)
    return None


def cc_index_prefix(coll, prefix):
    """Return list of CDX dicts for prefix (e.g. 'www.golfgalaxy.com/f/'), all pages. None on failure."""
    base = f"https://index.commoncrawl.org/{coll}-index"
    r = _get(base, {"url": prefix, "matchType": "prefix", "showNumPages": "true", "output": "json"})
    if r is None:
        return None
    if r.status_code == 404:
        return []
    try:
        n = json.loads(r.text)["pages"]
    except Exception:
        n = 1
    rows = []
    for p in range(n):
        r = _get(base, {"url": prefix, "matchType": "prefix", "output": "json", "page": p,
                        "fl": "status,timestamp,url,filename,offset,length,mime"})
        if r is None:
            return None
        if r.status_code == 404:
            break
        for l in r.text.splitlines():
            if l.startswith("{"):
                try:
                    rows.append(json.loads(l, strict=False))
                except Exception:
                    pass
        time.sleep(1)
    return rows
