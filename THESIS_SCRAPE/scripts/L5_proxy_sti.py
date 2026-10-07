"""L5: fetch DKS DEF 14A proxies (2023-2026) from EDGAR and extract annual-incentive (STI) payout / bonus passages.
Rerun: python THESIS_SCRAPE\\scripts\\L5_proxy_sti.py -> raw\\L5_proxy_<year>.txt (full text) + prints keyword passages.
"""
import requests, re, os
from bs4 import BeautifulSoup
H = {'User-Agent': 'DKS research palazzolojustin@gmail.com'}
RAW = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw'
docs = {'2026': '000108906326000015/dks-20260501.htm', '2025': '000108906325000054/dks-20250501.htm',
        '2024': '000108906324000060/dks-20240430.htm', '2023': '000108906323000076/dks-20230505.htm'}
pat = re.compile(r'(payout|% of target|percent of target|earned at|funded at|achievement|threshold|Annual Incentive|short-term incentive|STI)', re.I)
for y, d in docs.items():
    p = os.path.join(RAW, f'L5_proxy_{y}.txt')
    if not os.path.exists(p):
        url = 'https://www.sec.gov/Archives/edgar/data/1089063/' + d
        t = BeautifulSoup(requests.get(url, headers=H, timeout=60).text, 'html.parser').get_text(' ')
        t = re.sub(r'\s+', ' ', t)
        open(p, 'w', encoding='utf-8').write(t)
    t = open(p, encoding='utf-8').read()
    print('=====', y, len(t))
    for m in re.finditer(r'(?i)(payout of|paid out at|earned at|payout percentage|% of target|percent of target)', t):
        print('  ...', t[max(0, m.start()-300):m.end()+300].replace('\n', ' '))
