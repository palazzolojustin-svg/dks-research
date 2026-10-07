"""L4: EDGAR FTS for one phrase within one CIK, fetch docs (shared cache raw/L4_edgar_cache2), print sentences matching a regex.
Usage: python L4_cik_grep.py <cik> "<fts phrase>" "<sentence regex>" [startdt] [enddt] [forms]
Appends to raw/L4_cikgrep.txt
"""
import sys, re, time, requests
sys.path.insert(0, r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\scripts')
from L4_peer_sentences import get_text, H
cik, ph, rx = sys.argv[1], sys.argv[2], sys.argv[3]
sd = sys.argv[4] if len(sys.argv) > 4 else '2016-01-01'
ed = sys.argv[5] if len(sys.argv) > 5 else '2026-10-07'
forms = sys.argv[6] if len(sys.argv) > 6 else '10-K,10-Q,8-K'
hits, start = [], 0
while True:
    p = {'q': f'"{ph}"', 'forms': forms, 'dateRange': 'custom', 'startdt': sd, 'enddt': ed, 'ciks': cik.zfill(10), 'from': start}
    d = requests.get('https://efts.sec.gov/LATEST/search-index', params=p, headers=H, timeout=60).json()
    hh = d.get('hits', {}).get('hits', [])
    if not hh: break
    hits += [(x['_source']['file_date'], x['_source']['form'], x['_id'], x['_source']['ciks'][0]) for x in hh]
    start += len(hh)
    if start >= d['hits']['total']['value'] or start >= 200: break
out = open(r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\L4_cikgrep.txt', 'a', encoding='utf-8')
seen = set()
hdr = f'\n######## CIK {cik} | "{ph}" | /{rx}/ | {len(hits)} docs'
print(hdr); out.write(hdr + '\n')
for date, form, did, c in sorted(hits):
    adsh, fn = did.split(':')
    t = get_text(c, adsh, fn); url = t.split('\n', 1)[0]
    for s in re.split(r'(?<=[.;])\s+(?=[A-Z•])', t):
        if len(s) < 1500 and re.search(rx, s, re.I):
            k = re.sub(r'\W+', '', s.lower())[:300]
            if k in seen: continue
            seen.add(k)
            line = f'[{date} {form}] {url}\n   {s}'
            print(line); out.write(line + '\n')
out.close()
