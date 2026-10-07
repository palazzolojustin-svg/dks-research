"""B4: Wayback CDX census of stores.dickssportinggoods.com store pages.
For every store-page URL (/<st>/<city>/<storeno>/) get first and last capture timestamps and capture count.
First capture of a new store number ~ pre-opening/opening date; last capture of an old number ~ closure (relocation).
Rerun: python B4_wayback_stores.py  -> raw/B4_wayback_store_pages.csv
"""
import requests, re, csv, time, collections
H = {'User-Agent': 'DKS research script (contact: palazzolojustin@gmail.com)'}
OUT = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\B4_wayback_store_pages.csv'
pat = re.compile(r'stores\.dickssportinggoods\.com/([a-z]{2})/([^/]+)/(\d{1,5})/?$', re.I)
agg = collections.defaultdict(lambda: {'first': '99999999', 'last': '00000000', 'n': 0, 'ok': 0})
resume = None
page = 0
while True:
    url = ('https://web.archive.org/cdx/search/cdx?url=stores.dickssportinggoods.com/&matchType=prefix'
           '&fl=original,timestamp,statuscode&filter=mimetype:text/html&limit=50000&showResumeKey=true')
    if resume:
        url += '&resumeKey=' + requests.utils.quote(resume)
    for a in range(4):
        try:
            r = requests.get(url, headers=H, timeout=180)
            if r.status_code == 200:
                break
        except Exception as e:
            print('err', e)
        time.sleep(10 * (a + 1))
    lines = r.text.strip().split('\n')
    resume = None
    if len(lines) >= 2 and lines[-2].strip() == '':
        resume = lines[-1].strip(); lines = lines[:-2]
    for l in lines:
        p = l.split(' ')
        if len(p) < 3:
            continue
        m = pat.search(p[0].split('?')[0])
        if not m:
            continue
        k = (m.group(1).lower(), m.group(2).lower(), m.group(3))
        a_ = agg[k]
        a_['first'] = min(a_['first'], p[1][:8]); a_['last'] = max(a_['last'], p[1][:8]); a_['n'] += 1
        if p[2] == '200':
            a_['ok'] += 1
    page += 1
    print('page', page, len(lines), 'urls', len(agg), 'resume', bool(resume), flush=True)
    if not resume:
        break
    time.sleep(2)
with open(OUT, 'w', newline='', encoding='utf8') as f:
    w = csv.writer(f); w.writerow(['state', 'city', 'storeno', 'first', 'last', 'captures', 'captures_200'])
    for k, v in sorted(agg.items(), key=lambda x: int(x[0][2])):
        w.writerow([*k, v['first'], v['last'], v['n'], v['ok']])
print('done', len(agg))
