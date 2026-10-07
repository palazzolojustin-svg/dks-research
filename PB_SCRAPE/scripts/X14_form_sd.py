"""X14: pull every DKS Form SD (conflict minerals) from EDGAR and extract supplier-survey statistics
(number of vertical-brand suppliers surveyed / responding), a yearly count of in-scope vertical-brand suppliers.
Rerun: python X14_form_sd.py  -> raw/X14_formSD_<filingdate>.txt and printed snippets.
"""
import requests, re, os, time, json
from bs4 import BeautifulSoup
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'raw')
H = {'User-Agent': 'X14 research palazzolojustin-research@example.com'}
sub = requests.get('https://data.sec.gov/submissions/CIK0001089063.json', headers=H, timeout=60).json()
rec = sub['filings']['recent']
rows = [(rec['filingDate'][i], rec['accessionNumber'][i], rec['primaryDocument'][i]) for i in range(len(rec['form'])) if rec['form'][i] in ('SD', 'SD/A')]
for fd, acc, doc in sorted(rows):
    accn = acc.replace('-', '')
    idx = requests.get(f'https://www.sec.gov/Archives/edgar/data/1089063/{accn}/index.json', headers=H, timeout=60).json()
    texts = []
    for it in idx['directory']['item']:
        n = it['name']
        if n.lower().endswith(('.htm', '.html', '.txt')) and 'index' not in n.lower():
            h = requests.get(f'https://www.sec.gov/Archives/edgar/data/1089063/{accn}/{n}', headers=H, timeout=60).text
            texts.append(BeautifulSoup(h, 'html.parser').get_text(' ', strip=True))
            time.sleep(0.3)
    t = '\n\n'.join(texts)
    open(os.path.join(RAW, f'X14_formSD_{fd}.txt'), 'w', encoding='utf-8').write(t)
    print('=====', fd, acc, len(t))
    for m in re.finditer(r'(?i)(\d[\d,]*\s*(?:%|percent)?[^.]{0,80}(?:suppliers|vendors|factories)[^.]{0,200}\.)', t):
        print('  -', m.group(1)[:330])
    time.sleep(0.5)
