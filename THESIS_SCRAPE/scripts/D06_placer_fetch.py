"""D06: fetch Placer.ai Anchor article(s) with plain requests (public pages) and print article body only.
Usage: python THESIS_SCRAPE/scripts/D06_placer_fetch.py <url-or-slug> [...]
       python THESIS_SCRAPE/scripts/D06_placer_fetch.py --links <url>   (list anchor article links on a page)
Saves text to THESIS_SCRAPE/raw/D06_placer_<slug>.txt
"""
import sys, os, re, requests
from bs4 import BeautifulSoup
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36'}
args = sys.argv[1:]
if args and args[0] == '--links':
    r = requests.get(args[1], headers=H, timeout=40)
    s = BeautifulSoup(r.text, 'html.parser')
    seen = set()
    for a in s.find_all('a', href=True):
        h = a['href']
        if '/anchor/articles/' in h and h not in seen:
            seen.add(h); print(h)
    sys.exit()
for u in args:
    if not u.startswith('http'):
        u = 'https://www.placer.ai/anchor/articles/' + u
    r = requests.get(u, headers=H, timeout=40)
    t = BeautifulSoup(r.text, 'html.parser').get_text(' ', strip=True)
    i = t.find('Log In Article')
    j = t.find('The New Tenant Mix Playbook Read the report', i if i > 0 else 0)
    body = t[i:j] if i > 0 else t[:3000]
    slug = u.rstrip('/').split('/')[-1][:60]
    open(os.path.join(BASE, 'raw', f'D06_placer_{slug}.txt'), 'w', encoding='utf-8').write(u + '\n' + body)
    print('=====', u, r.status_code); print(body[:8000])
