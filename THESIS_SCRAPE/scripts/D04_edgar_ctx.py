"""D04: fetch specific EDGAR documents and print context around DICK'S mentions.
Usage: python D04_edgar_ctx.py <cik> <adsh:filename> [keyword] [window]"""
import sys, re, requests
from bs4 import BeautifulSoup
H = {'User-Agent': 'DKS research palazzolojustin@gmail.com'}
cik = sys.argv[1].lstrip('0'); adsh, fn = sys.argv[2].split(':')
kw = sys.argv[3] if len(sys.argv) > 3 else r"Dick.s"
win = int(sys.argv[4]) if len(sys.argv) > 4 else 500
url = f'https://www.sec.gov/Archives/edgar/data/{cik}/{adsh.replace("-", "")}/{fn}'
r = requests.get(url, headers=H, timeout=60)
t = BeautifulSoup(r.text, 'html.parser').get_text(' ', strip=True)
print(url, r.status_code, len(t))
last = -10**9
for m in re.finditer(kw, t, re.I):
    if m.start() - last < win:
        continue
    last = m.start()
    print('---', t[max(0, m.start() - win): m.end() + win])
