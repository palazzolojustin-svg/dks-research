"""V2: Wayback second source. Usage: python3 V2_wb_extract.py <label> <cdx.json> <ts_from> <ts_to> [max] ; reuses V2_cc_extract.process with a Wayback fetch."""
import json, os, sys, time, random, threading
from concurrent.futures import ThreadPoolExecutor
import requests
sys.path.insert(0, os.path.dirname(__file__))
import V2_cc_extract as X
S = requests.Session()
def wfetch(rec):
    u = f"https://web.archive.org/web/{rec['timestamp']}id_/{rec['url']}"
    for i in range(4):
        try:
            r = S.get(u, timeout=90)
            if r.status_code == 200: return r.text
        except Exception: pass
        time.sleep(3 + 3 * i)
    return None
X.fetch = wfetch
label, cdxf, a, b = sys.argv[1:5]; mx = int(sys.argv[5]) if len(sys.argv) > 5 else 100000
rows = json.load(open(cdxf))[1:]
rows = [{"url": r[2], "timestamp": r[1]} for r in rows if a <= r[1] <= b and "?" not in r[2]]
seen = {}
for r in rows: seen.setdefault(r["url"].lower(), r)
rows = list(seen.values()); random.Random(11).shuffle(rows); rows = rows[:mx]
os.makedirs(X.OUT, exist_ok=True)
print(label, "to fetch", len(rows), flush=True)
with open(os.path.join(X.OUT, f"WB-{label}_pages.jsonl"), "a") as fp, open(os.path.join(X.OUT, f"WB-{label}_products.jsonl"), "a") as fprod:
    with ThreadPoolExecutor(5) as ex:
        list(ex.map(lambda r: X.process(r, "WB-" + label, fp, fprod), rows))
print(label, "done", flush=True)
