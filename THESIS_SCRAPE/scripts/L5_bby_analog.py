"""L5: Best Buy store-workforce analog (coordinator lead; L4 owns the full peer table).
Pulls Best Buy (CIK 764478) 10-K filings FY2019-FY2025 from EDGAR, extracts the human-capital employee counts and
SG&A/labor sentences. Rerun: python THESIS_SCRAPE\\scripts\\L5_bby_analog.py -> raw\\L5_bby_10k_<fy>.txt, raw\\L5_bby_extract.txt
"""
import requests, re, os, time
from bs4 import BeautifulSoup
H = {'User-Agent': 'DKS research palazzolojustin@gmail.com'}
RAW = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw'
j = requests.get('https://data.sec.gov/submissions/CIK0000764478.json', headers=H, timeout=30).json()
f = j['filings']['recent']
tenk = [(d, a, p) for fm, d, a, p in zip(f['form'], f['filingDate'], f['accessionNumber'], f['primaryDocument']) if fm == '10-K' and d >= '2019-01-01']
out = []
kw = re.compile(r'(?i)(employ(ed|ees) approximately|approximately [0-9,]+ (full-time|part-time|employees)|full-time.{0,40}part-time|'
                r'store payroll|labor|workforce|operating model|headcount|restructuring)')
for d, a, p in sorted(tenk):
    path = os.path.join(RAW, f'L5_bby_10k_{d}.txt')
    if not os.path.exists(path):
        url = f"https://www.sec.gov/Archives/edgar/data/764478/{a.replace('-', '')}/{p}"
        t = re.sub(r'\s+', ' ', BeautifulSoup(requests.get(url, headers=H, timeout=90).text, 'html.parser').get_text(' '))
        open(path, 'w', encoding='utf-8').write(t); time.sleep(0.5)
    t = open(path, encoding='utf-8').read()
    out.append(f'===== 10-K filed {d} ({len(t)} chars)')
    seen = set()
    for m in kw.finditer(t):
        s = t[max(0, m.start() - 250): m.end() + 350]
        k = s[:80]
        if k in seen: continue
        seen.add(k); out.append('  ... ' + s)
open(os.path.join(RAW, 'L5_bby_extract.txt'), 'w', encoding='utf-8').write('\n'.join(out))
print('\n'.join(o for o in out if o.startswith('=====') or re.search(r'(?i)approximately [0-9,]+ (full|part|employ)|employed approximately|employ(ed|ees) approx', o)))
