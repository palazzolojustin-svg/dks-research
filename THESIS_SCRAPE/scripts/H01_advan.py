"""H01: crawl Advan Research public 'insights' posts (sitemap + listing), save text of posts mentioning DICK'S /
House of Sport / Academy / sporting goods to raw/H01_advan/<slug>.txt and print matching lines.
Rerun: python H01_advan.py
"""
import requests, re, os, time
from bs4 import BeautifulSoup
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, 'raw', 'H01_advan'); os.makedirs(OUT, exist_ok=True)
H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'}
PAT = re.compile(r"Dick|House of Sport|Academy Sports|sporting goods|Foot Locker|Scheels", re.I)
urls = set()
for p in ['https://advanresearch.com/sitemap.xml', 'https://advanresearch.com/insights']:
    try:
        r = requests.get(p, headers=H, timeout=40)
        print(p, r.status_code, len(r.text))
        for u in re.findall(r'https://advanresearch\.com/insights/[A-Za-z0-9\-]+', r.text):
            urls.add(u)
        for u in re.findall(r'href="(/insights/[A-Za-z0-9\-]+)"', r.text):
            urls.add('https://advanresearch.com' + u)
    except Exception as e:
        print('ERR', p, e)
print(len(urls), 'insight urls')
open(os.path.join(BASE, 'raw', 'H01_advan_insights_urls.txt'), 'w').write('\n'.join(sorted(urls)))
for u in sorted(urls):
    try:
        r = requests.get(u, headers=H, timeout=40)
    except Exception as e:
        print('ERR', u); continue
    s = BeautifulSoup(r.text, 'html.parser')
    for t in s(['script', 'style', 'nav', 'footer']):
        t.decompose()
    tx = s.get_text('\n', strip=True)
    hits = [l for l in tx.split('\n') if PAT.search(l) and len(l) > 20]
    if hits:
        slug = u.rstrip('/').split('/')[-1][:100]
        open(os.path.join(OUT, slug + '.txt'), 'w', encoding='utf-8').write(u + '\n\n' + tx)
        m = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2}, 20\d\d', tx)
        print('#####', u, m.group(0) if m else '')
        for h in hits[:8]:
            print('   >', h[:400])
    time.sleep(1)
