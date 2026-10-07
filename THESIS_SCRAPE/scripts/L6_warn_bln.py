"""L6: Download Big Local News (Stanford) consolidated WARN data from GitHub
(biglocalnews/warn-github-flow, branch 'transformer') and grep for DICK'S / Golf Galaxy /
Going Going Gone / Foot Locker / Public Lands / GameChanger.
Rerun: python THESIS_SCRAPE\\scripts\\L6_warn_bln.py
Outputs: THESIS_SCRAPE\\raw\\L6_bln_consolidated.csv (cache), L6_bln_hits.csv, L6_bln_branch_dates.txt
"""
import requests, time, os, re, csv, io, sys
H = {'User-Agent': 'DKS research palazzolojustin@gmail.com'}
RAW = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw'
BASE = 'https://raw.githubusercontent.com/biglocalnews/warn-github-flow/transformer/data/warn-transformer/'

def get(u, tries=6):
    for i in range(tries):
        try:
            r = requests.get(u, headers=H, timeout=120)
            if r.status_code == 200:
                return r
            print('status', r.status_code, u)
        except Exception as e:
            print('err', type(e).__name__, u)
        time.sleep(3 + 2 * i)
    return None

PAT = re.compile(r"dick'?s sporting|dicks sporting|dick s sporting|golf galaxy|going,? going,? gone|foot ?locker|public lands|gamechanger|game changer|champs sports|eastbay|dsg |dick's|dicks inc", re.I)

def main():
    cache = os.path.join(RAW, 'L6_bln_consolidated.csv')
    if not os.path.exists(cache) or '--refresh' in sys.argv:
        r = get(BASE + 'processed/consolidated.csv')
        open(cache, 'wb').write(r.content)
    txt = open(cache, encoding='utf-8', errors='replace').read()
    rdr = csv.DictReader(io.StringIO(txt))
    rows = list(rdr)
    print('rows', len(rows), 'cols', rdr.fieldnames)
    hits = [r for r in rows if PAT.search(' '.join(str(v) for v in r.values()))]
    with open(os.path.join(RAW, 'L6_bln_hits.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=rdr.fieldnames)
        w.writeheader(); w.writerows(hits)
    print('hits', len(hits))
    for h in hits:
        print({k: h[k] for k in rdr.fieldnames if h[k]})
    # data freshness per state: max notice date
    from collections import defaultdict
    mx = defaultdict(str)
    for r in rows:
        d = r.get('notice_date') or ''
        if d > mx[r.get('postal_code', '')]:
            mx[r.get('postal_code', '')] = d
    with open(os.path.join(RAW, 'L6_bln_state_maxdate.txt'), 'w') as f:
        for k in sorted(mx):
            f.write(f'{k}\t{mx[k]}\n')
    print(dict(mx))

if __name__ == '__main__':
    main()
