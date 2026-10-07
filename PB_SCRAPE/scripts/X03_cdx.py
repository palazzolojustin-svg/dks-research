"""X03 helper: query the Wayback Machine CDX API (throttled, retries).

Usage:
  python X03_cdx.py "<url pattern>" [from] [to] [extra k=v ...] > out.txt
Examples:
  python X03_cdx.py "www.dickssportinggoods.com/f/calia*" 2022 2026 collapse=urlkey
  python X03_cdx.py "www.dickssportinggoods.com/" 2025 2026 collapse=timestamp:8
Prints one line per capture: timestamp original statuscode length mimetype
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from X03_wb import get


def cdx(url, frm=None, to=None, **extra):
    params = {"url": url, "output": "json", "fl": "timestamp,original,statuscode,length,mimetype"}
    if frm:
        params["from"] = frm
    if to:
        params["to"] = to
    params.update(extra)
    r = get("https://web.archive.org/cdx/search/cdx", params=params, timeout=240)
    if r is None or r.status_code != 200:
        return None
    txt = r.text.strip()
    if not txt:
        return []
    d = r.json()
    return d[1:] if d and d[0][0] == "timestamp" else d


if __name__ == "__main__":
    url = sys.argv[1]
    frm = sys.argv[2] if len(sys.argv) > 2 else None
    to = sys.argv[3] if len(sys.argv) > 3 else None
    extra = dict(a.split("=", 1) for a in sys.argv[4:])
    rows = cdx(url, frm, to, **extra)
    if rows is None:
        print("# FAILED")
        sys.exit(1)
    for row in rows:
        print(" ".join(row))
