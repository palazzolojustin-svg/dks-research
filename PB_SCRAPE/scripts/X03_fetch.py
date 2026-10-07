"""X03: fetch a raw Wayback snapshot (id_ mode, no Wayback toolbar) with throttling and local cache.
Usage: python X03_fetch.py <timestamp> <url>   -> prints length
Import: from X03_fetch import fetch; html = fetch(ts, url)
"""
import os, sys, hashlib
sys.path.insert(0, os.path.dirname(__file__))
from X03_wb import get

CACHE = os.path.join(os.path.dirname(__file__), "..", "raw", "X03_cache")
os.makedirs(CACHE, exist_ok=True)


def fetch(ts, url):
    key = hashlib.md5(f"{ts} {url}".encode()).hexdigest()
    fn = os.path.join(CACHE, key + ".html")
    if os.path.exists(fn):
        return open(fn, encoding="utf-8", errors="replace").read()
    r = get(f"https://web.archive.org/web/{ts}id_/{url}", timeout=120)
    if r is None or r.status_code != 200:
        return None
    r.encoding = r.encoding or "utf-8"
    t = r.text
    open(fn, "w", encoding="utf-8").write(t)
    return t


if __name__ == "__main__":
    t = fetch(sys.argv[1], sys.argv[2])
    print(len(t) if t else "FAIL")
