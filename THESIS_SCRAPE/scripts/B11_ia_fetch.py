"""B11: download Iowa DOR Quarterly Retail Sales and Use Tax Reports (city x business group) listed on revenue.iowa.gov/resources/reports (topic 60), all pages.
Rerun: python scripts/B11_ia_fetch.py -> raw/B11_cache/ia/"""
import requests, re, os, time
from bs4 import BeautifulSoup
H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124'}
OUT = 'raw/B11_cache/ia'; os.makedirs(OUT, exist_ok=True)
for page in range(0, 6):
    r = requests.get(f'https://revenue.iowa.gov/resources/reports?field_topic_target_id=60&year=All&page={page}', headers=H, timeout=60)
    s = BeautifulSoup(r.text, 'html.parser'); n = 0
    for a in s.find_all('a', href=True):
        t = a.get_text(' ', strip=True)
        m = re.search(r'Quarter Ending (\w+) (\d{4})', t)
        if m and '/media/' in a['href']:
            ext = 'xlsx' if 'xlsx' in t else ('xls' if 'xls' in t else 'pdf')
            fn = f"{OUT}/{m.group(2)}_{m.group(1)}.{ext}"
            n += 1
            if os.path.exists(fn): continue
            b = requests.get('https://revenue.iowa.gov' + a['href'].replace('?inline', ''), headers=H, timeout=120).content
            open(fn, 'wb').write(b); print(fn, len(b)); time.sleep(0.5)
    print('page', page, n)
    if n == 0: break
