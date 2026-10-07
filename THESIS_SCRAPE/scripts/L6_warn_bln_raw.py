"""L6: Download every Big Local News raw per-state WARN CSV (branch 'transformer' of
biglocalnews/warn-github-flow, updated 2026-10-06) and grep all columns for DKS-family names.
Also reports per-state row count and date range (any YYYY or MM/DD/YYYY values) so coverage gaps are visible.
Rerun: python THESIS_SCRAPE\\scripts\\L6_warn_bln_raw.py   (add --refresh to re-download)
Outputs: THESIS_SCRAPE\\raw\\L6_bln_raw\\<st>.csv, raw\\L6_bln_raw_hits.txt, raw\\L6_bln_raw_coverage.txt
"""
import requests, time, os, re, csv, io, sys
H = {'User-Agent': 'DKS research palazzolojustin@gmail.com'}
RAW = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw'
D = os.path.join(RAW, 'L6_bln_raw'); os.makedirs(D, exist_ok=True)
BASE = 'https://raw.githubusercontent.com/biglocalnews/warn-github-flow/transformer/data/warn-transformer/raw/'
STATES = 'ak al az ca co ct dc de fl ga hi ia id il in ks ky la ma md me mi mo ms mt nd ne nj ny oh ok or pa ri sc sd tn tx ut va vt wa wi'.split()
PAT = re.compile(r"dick.{0,2}s\s*sporting|golf\s*galaxy|going,?\s*going,?\s*gone|foot\s*locker|footlocker|public\s*lands|gamechanger|champs\s*sports|eastbay|\bdsg\b|dick.{0,2}s,?\s*inc|world\s*sports\s*shop|\bwss\b|lids\b|kids\s*foot\s*locker", re.I)
DATE = re.compile(r'\b(20\d\d)-(\d\d)-(\d\d)\b|\b(\d{1,2})/(\d{1,2})/(20\d\d)\b')

def get(u, tries=6):
    for i in range(tries):
        try:
            r = requests.get(u, headers=H, timeout=120)
            if r.status_code == 200:
                return r
        except Exception as e:
            print('err', type(e).__name__, u)
        time.sleep(3 + 2 * i)
    return None

out, cov = [], []
for st in STATES:
    p = os.path.join(D, st + '.csv')
    if not os.path.exists(p) or '--refresh' in sys.argv:
        r = get(BASE + st + '.csv')
        if r is None:
            cov.append(f'{st}\tDOWNLOAD FAILED'); continue
        open(p, 'wb').write(r.content)
    txt = open(p, encoding='utf-8', errors='replace').read()
    rows = list(csv.reader(io.StringIO(txt)))
    hdr = rows[0] if rows else []
    dates = []
    for row in rows[1:]:
        line = ' | '.join(row)
        for m in DATE.finditer(line):
            if m.group(1):
                dates.append(f'{m.group(1)}-{m.group(2)}-{m.group(3)}')
            else:
                dates.append(f'{m.group(6)}-{int(m.group(4)):02d}-{int(m.group(5)):02d}')
        if PAT.search(line):
            out.append(f'{st.upper()}\t' + ' | '.join(f'{h}={v}' for h, v in zip(hdr, row) if v.strip()))
    dates = [d for d in dates if '2000' < d < '2027-12']
    n26 = sum(1 for d in dates if d.startswith('2026'))
    cov.append(f'{st}\trows={len(rows)-1}\tmin={min(dates) if dates else None}\tmax={max(dates) if dates else None}\tdates_in_2026={n26}\tcols={hdr[:8]}')
open(os.path.join(RAW, 'L6_bln_raw_hits.txt'), 'w', encoding='utf-8').write('\n'.join(out))
open(os.path.join(RAW, 'L6_bln_raw_coverage.txt'), 'w', encoding='utf-8').write('\n'.join(cov))
print('\n'.join(cov)); print('HITS', len(out)); print('\n'.join(out))
