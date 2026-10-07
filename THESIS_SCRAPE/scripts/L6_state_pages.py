"""L6: fetch state WARN HTML pages / files not fully covered by the Big Local News archive and grep for
DKS-family names. Usage: python L6_state_pages.py <url> [<url> ...]
Saves each page to THESIS_SCRAPE\\raw\\L6_state\\<sanitised>.(html|bin) and prints hits + crude size stats.
"""
import requests, re, os, sys, time
H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) research palazzolojustin@gmail.com'}
D = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\L6_state'; os.makedirs(D, exist_ok=True)
PAT = re.compile(r"(?i).{0,160}(dick.{0,2}s\s*sporting|golf\s*galaxy|going,?\s*going|foot\s*locker|footlocker|public\s*lands|champs\s*sports).{0,160}")
for u in sys.argv[1:]:
    try:
        r = requests.get(u, headers=H, timeout=90)
    except Exception as e:
        print('ERR', u, e); continue
    name = re.sub(r'[^A-Za-z0-9]+', '_', u)[-120:]
    ct = r.headers.get('content-type', '')
    ext = '.html' if 'html' in ct else '.bin'
    open(os.path.join(D, name + ext), 'wb').write(r.content)
    t = r.text if 'html' in ct or 'text' in ct or 'json' in ct else ''
    print(u, r.status_code, ct, len(r.content), 'tr=', t.count('<tr'))
    if 'captcha' in t.lower() or 'challenge' in t.lower()[:3000]:
        print('  POSSIBLE CHALLENGE PAGE')
    for m in PAT.finditer(t):
        print('  HIT', re.sub(r'<[^>]+>', ' ', re.sub(r'\s+', ' ', m.group(0))))
    links = re.findall(r'href="([^"]+\.(?:xlsx|xls|csv|pdf)[^"]*)"', t, re.I)
    if links:
        print('  files:', links[:40])
    time.sleep(1)
