"""H06: download archived dickssportinggoods.jobs job sitemaps (Wayback) and build title censuses over time.
Each sitemap <loc> is /job/<title-slug>/<location-slug>/<reqid>/ so the full open-posting title mix at each snapshot can be counted.
Rerun: python H06_wayback_sitemaps.py -> raw/H06_sitemap_<ts>.txt (urls) and raw/H06_sitemap_census.csv
"""
import requests, re, time, os, csv
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'raw')
H = {'User-Agent': 'Mozilla/5.0 research'}


def get(u, tries=5):
    for a in range(tries):
        try:
            r = requests.get(u, headers=H, timeout=120)
            if r.status_code == 200:
                return r.text
            print('status', r.status_code, u)
        except Exception as e:
            print('err', str(e)[:80])
        time.sleep(15 * (a + 1))
    return None


cdx = get('http://web.archive.org/cdx/search/cdx?url=dickssportinggoods.jobs/&matchType=prefix&output=txt&fl=timestamp,original,statuscode&filter=statuscode:200&filter=original:.*sitemap.*&collapse=digest&from=2024')
lines = [l.split() for l in (cdx or '').splitlines()]
print(len(lines))
for l in lines:
    print(l)
open(os.path.join(RAW, 'H06_sitemap_cdx.txt'), 'w').write(cdx or '')
rows = []
for ts, orig, sc in lines:
    if 'job' not in orig:
        continue
    t = get(f'http://web.archive.org/web/{ts}id_/{orig}')
    if not t:
        continue
    locs = re.findall(r'<loc>([^<]+)</loc>', t)
    jobs = [l for l in locs if '/job/' in l]
    subs = [l for l in locs if l.endswith('.xml')]
    open(os.path.join(RAW, f'H06_sitemap_{ts}.txt'), 'w', encoding='utf-8').write('\n'.join(locs))
    rows.append([ts, orig, len(locs), len(jobs), len(subs)])
    print(ts, orig, len(locs), len(jobs), len(subs), flush=True)
    time.sleep(3)
with open(os.path.join(RAW, 'H06_sitemap_census.csv'), 'w', newline='') as fh:
    w = csv.writer(fh); w.writerow(['ts', 'url', 'n_locs', 'n_jobs', 'n_subsitemaps']); w.writerows(rows)
