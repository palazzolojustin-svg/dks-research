"""X03: Common Crawl index + WARC record fetch (alternative to Wayback when web.archive.org rate-limits).

  python X03_cc.py index <collection> "<url pattern>"      -> prints JSON lines (status, timestamp, url, filename, offset, length)
  python X03_cc.py fetch <filename> <offset> <length> out.html
Import: from X03_cc import cc_index, cc_fetch
Common Crawl crawls roughly monthly (collection ids CC-MAIN-YYYY-WW, list at https://index.commoncrawl.org/collinfo.json).
"""
import sys, json, gzip, io, time, requests

UA = {"User-Agent": "Mozilla/5.0 (research; DKS study)"}


def cc_index(coll, url, filt=None):
    params = {"url": url, "output": "json"}
    if filt:
        params["filter"] = filt
    for a in range(5):
        try:
            r = requests.get(f"https://index.commoncrawl.org/{coll}-index", params=params, headers=UA, timeout=180)
            if r.status_code == 404:
                return []
            if r.status_code == 200:
                return [json.loads(l) for l in r.text.splitlines() if l.strip()]
            print("cc idx", r.status_code, file=sys.stderr)
        except Exception as e:
            print("cc idx err", e, file=sys.stderr)
        time.sleep(10 * (a + 1))
    return None


def cc_fetch(filename, offset, length):
    offset, length = int(offset), int(length)
    for a in range(5):
        try:
            r = requests.get("https://data.commoncrawl.org/" + filename,
                             headers={**UA, "Range": f"bytes={offset}-{offset + length - 1}"}, timeout=180)
            if r.status_code in (200, 206):
                raw = gzip.GzipFile(fileobj=io.BytesIO(r.content)).read()
                # WARC header \r\n\r\n HTTP header \r\n\r\n body
                parts = raw.split(b"\r\n\r\n", 2)
                body = parts[2] if len(parts) == 3 else raw
                return body.decode("utf-8", "replace")
            print("cc fetch", r.status_code, file=sys.stderr)
        except Exception as e:
            print("cc fetch err", e, file=sys.stderr)
        time.sleep(10 * (a + 1))
    return None


if __name__ == "__main__":
    if sys.argv[1] == "index":
        rows = cc_index(sys.argv[2], sys.argv[3])
        for r in rows or []:
            print(json.dumps({k: r.get(k) for k in ("status", "timestamp", "url", "filename", "offset", "length")}))
    else:
        t = cc_fetch(sys.argv[2], sys.argv[3], sys.argv[4])
        open(sys.argv[5], "w", encoding="utf-8").write(t or "")
        print(len(t or ""))
