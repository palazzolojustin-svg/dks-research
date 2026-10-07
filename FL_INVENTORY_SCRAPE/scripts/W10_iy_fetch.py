"""W10: polite ImportYeti fetcher (free public pages, no login) via curl_cffi chrome impersonation.
Usage: python3 W10_iy_fetch.py company foot-locker [more slugs]; python3 W10_iy_fetch.py supplier <slug>
Saves decoded Next.js RSC payload to FL_INVENTORY_SCRAPE/raw/W10/iy_<kind>_<slug>.txt (cache: skip if exists and >20KB)."""
import re, sys, os, time
from curl_cffi import requests
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "raw", "W10")
SPACING = 12

def decode(html):
    chunks = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)</script>', html, re.S)
    big = "".join(chunks).encode().decode("unicode_escape", errors="ignore")
    try: big = big.encode("latin-1", errors="ignore").decode("utf-8", errors="ignore")
    except Exception: pass
    return big

def path_for(kind, slug):
    return os.path.join(RAW, f"iy_{kind}_{re.sub(r'[^A-Za-z0-9_-]+','_',slug)[:80]}.txt")

def fetch(kind, slug, force=False):
    p = path_for(kind, slug)
    if os.path.exists(p) and os.path.getsize(p) > 20000 and not force:
        return open(p, encoding="utf-8").read(), "cached"
    url = f"https://www.importyeti.com/{kind}/{slug}"
    for attempt in range(3):
        try:
            r = requests.get(url, impersonate="chrome", timeout=60)
            big = decode(r.text); code = r.status_code
        except Exception as e:
            big, code = "", f"ERR {e}"
        if "Over Time" in big:
            open(p, "w", encoding="utf-8").write(big); time.sleep(SPACING); return big, code
        if code == 404 or "4 Not Found" in big:
            time.sleep(SPACING); return "", f"404"
        time.sleep(60 * (attempt + 1))
    return "", f"fail {code}"

if __name__ == "__main__":
    kind = sys.argv[1]
    for s in sys.argv[2:]:
        big, st = fetch(kind, s)
        print(kind, s, st, len(big), flush=True)
