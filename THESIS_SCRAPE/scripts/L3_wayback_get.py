"""L3: fetch a list of Wayback snapshots (raw id_ mode) to raw/L3_wb_<ts>_<slug>.txt. Resumable.
Usage: python L3_wayback_get.py <ts> <url> [<ts> <url> ...]
"""
import requests, sys, os, re, time
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'raw')
H = {'User-Agent': 'Mozilla/5.0 research (DKS thesis L3)'}
a = sys.argv[1:]
for ts, url in zip(a[::2], a[1::2]):
    slug = re.sub(r'[^A-Za-z0-9]+', '_', url.split('//')[-1])[:80]
    fn = os.path.join(RAW, f'L3_wb_{ts}_{slug}.txt')
    if os.path.exists(fn) and os.path.getsize(fn) > 0:
        print('have', fn); continue
    for k in range(8):
        try:
            r = requests.get(f'https://web.archive.org/web/{ts}id_/{url}', headers=H, timeout=120)
            if r.status_code == 200:
                open(fn, 'w', encoding='utf-8').write(r.text)
                print('ok', ts, url, len(r.text), flush=True)
                break
            print('status', r.status_code, ts, url)
            if r.status_code == 404:
                break
        except Exception as e:
            print('err', str(e)[:80])
        time.sleep(min(60, 8 * (k + 1)))
    time.sleep(2)
