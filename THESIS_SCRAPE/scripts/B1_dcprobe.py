"""B1: probe a CivicPlus DocumentCenter ID range and log filenames (no full download).
Rerun: python B1_dcprobe.py https://braintreema.gov 16470 17900 out.txt
Writes "id status content-type filename" per line; filename from Content-Disposition or final URL.
"""
import sys, re, time, requests
from concurrent.futures import ThreadPoolExecutor
H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/127.0'}
base, a, b, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]

def probe(i):
    u = f'{base}/DocumentCenter/View/{i}'
    for k in range(3):
        try:
            with requests.get(u, headers=H, timeout=60, stream=True) as r:
                cd = r.headers.get('content-disposition', '')
                m = re.search(r'filename\*?=(?:UTF-8\'\')?"?([^";]+)', cd)
                name = m.group(1) if m else r.url
                return f'{i} {r.status_code} {r.headers.get("content-type","")[:30]} {name}'
        except Exception as e:
            time.sleep(3)
    return f'{i} ERR'

with ThreadPoolExecutor(4) as ex, open(out, 'w', encoding='utf-8') as f:
    for line in ex.map(probe, range(a, b)):
        f.write(line + '\n'); f.flush()
