"""W04 Wayback helpers with backoff (archive.org is shared/rate-limited)."""
import time, json, subprocess, os, hashlib

CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "raw", "W04", "wbcache")
os.makedirs(CACHE, exist_ok=True)

def _curl(url, timeout=120):
    p = subprocess.run(["curl", "-sS", "-L", "--compressed", "-m", str(timeout), "-w", "\n%{http_code}", url], capture_output=True)
    out = p.stdout
    try:
        body, code = out.rsplit(b"\n", 1); code = int(code)
    except Exception:
        body, code = out, 0
    return code, body

def fetch(url, tries=6, cache=True):
    key = os.path.join(CACHE, hashlib.md5(url.encode()).hexdigest())
    if cache and os.path.exists(key):
        return open(key, "rb").read()
    delay = 5
    for i in range(tries):
        code, body = _curl(url)
        if code == 200 and body:
            if cache: open(key, "wb").write(body)
            return body
        if code == 404: return None
        time.sleep(delay); delay = min(delay * 2, 90)
    return None

def cdx(url, frm="2023", to="2026", extra=""):
    q = f"https://web.archive.org/cdx/search/cdx?url={url}&output=json&from={frm}&to={to}&fl=timestamp,original,statuscode,length{extra}"
    b = fetch(q)
    if not b: return []
    try:
        d = json.loads(b)
    except Exception:
        return []
    return d[1:]

def snap(ts, url):
    return fetch(f"https://web.archive.org/web/{ts}id_/{url}")
