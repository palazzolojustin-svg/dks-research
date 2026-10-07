"""X06: fetch archived job-description text for selected requisition numbers from the Wayback Machine.

Rerun: python X06_wayback_jd.py 202509469 202606441 ...
Output: PB_SCRAPE/raw/X06_wayback_jd_<req>.txt (cleaned text) ; prints first ~3000 chars.
Uses the CDX list in raw/X06_wayback_joburls.csv to find the archived URL(s) for each req, then fetches
https://web.archive.org/web/<timestamp>id_/<url> (raw archived HTML) and strips tags.
For Workday (JS-rendered) captures, it tries the CXS JSON path instead (rarely archived).
"""
import csv, os, re, sys, time, html, requests

RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'raw')
rows = list(csv.DictReader(open(os.path.join(RAW, 'X06_wayback_joburls.csv'), encoding='utf8')))
H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36'}


def clean(t):
    t = re.sub(r'(?is)<(script|style|noscript)[^>]*>.*?</\1>', ' ', t)
    t = re.sub(r'<[^>]+>', ' ', t)
    return re.sub(r'\s+', ' ', html.unescape(t)).strip()


for req in sys.argv[1:]:
    cands = [r for r in rows if req in r['url'] and r['status'] in ('200', '-', '')]
    cands = sorted(cands, key=lambda r: ('myworkdayjobs' in r['url'], r['first_capture']))
    got = None
    for c in cands[:4]:
        u = 'https://web.archive.org/web/%sid_/%s' % (c['first_capture'] + '000000' if len(c['first_capture']) == 8 else c['first_capture'], c['url'])
        # need full timestamp; query CDX for exact one
        try:
            q = requests.get('https://web.archive.org/cdx/search/cdx', params={'url': c['url'], 'output': 'json', 'limit': '3'}, headers=H, timeout=60).json()
            if len(q) > 1:
                ts = q[1][1]
                u = 'https://web.archive.org/web/%sid_/%s' % (ts, q[1][2])
            r = requests.get(u, headers=H, timeout=60)
            txt = clean(r.text)
            if len(txt) > 800 and ('Responsibilities' in txt or 'QUALIFICATIONS' in txt.upper() or 'OVERVIEW' in txt.upper()):
                got = (u, txt)
                break
        except Exception as e:
            print('err', e)
        time.sleep(1.5)
    if got:
        open(os.path.join(RAW, 'X06_wayback_jd_%s.txt' % req), 'w', encoding='utf8').write(got[0] + '\n' + got[1])
        t = got[1]
        i = t.upper().find('OVERVIEW')
        print('=====', req, got[0])
        print(t[max(0, i - 200): i + 3500] if i >= 0 else t[:3500])
    else:
        print('=====', req, 'NO TEXT', [c['url'] for c in cands[:3]])
