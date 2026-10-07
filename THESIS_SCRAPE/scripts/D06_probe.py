"""D06 scratch probe: fetch a URL with a browser UA, save HTML, list candidate data/API URLs and keyword hits.
Usage: python THESIS_SCRAPE/scripts/D06_probe.py <url> <outname> [keyword ...]
"""
import sys, re, os, requests
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36'}
u, name = sys.argv[1], sys.argv[2]
kws = sys.argv[3:]
r = requests.get(u, headers=H, timeout=60)
t = r.text
print(r.status_code, len(t))
open(os.path.join(BASE, 'raw', f'D06_{name}'), 'w', encoding='utf-8').write(t)
urls = sorted(set(re.findall(r'https?://[^"\'\s<>]*(?:api|data|json)[^"\'\s<>]*', t)))
print('candidate urls:', urls[:40])
for k in kws:
    for m in list(re.finditer(re.escape(k), t, re.I))[:6]:
        print(f'[{k}]', t[max(0, m.start() - 200): m.start() + 300].replace('\n', ' '))
