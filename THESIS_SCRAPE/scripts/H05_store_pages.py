"""H05: scrape every DKS store page from stores.dickssportinggoods.com sitemap.
Extracts store number, name, address, lat/lng, containedIn (mall), feature list, and flags for
House of Sport / Field House text. Output: THESIS_SCRAPE/raw/H05_dks_store_pages.csv
Rerun: python THESIS_SCRAPE/scripts/H05_store_pages.py   (needs raw/H05_dks_store_sitemap.txt; ~800 requests, 4 threads)
"""
import requests, re, json, csv, time
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

BASE = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw'
h = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36'}
locs = [l for l in open(BASE + r'\H05_dks_store_sitemap.txt').read().split('\n') if len(l.split('/')) == 7]


def get(url):
    for i in range(3):
        try:
            r = requests.get(url, headers=h, timeout=30)
            if r.status_code == 200:
                return r.text
        except Exception:
            pass
        time.sleep(2)
    return None


def parse(url):
    html = get(url)
    row = {'url': url, 'store_no': url.rstrip('/').split('/')[-1], 'state': url.split('/')[3], 'city_slug': url.split('/')[4]}
    if not html:
        row['err'] = 'fetch'
        return row
    soup = BeautifulSoup(html, 'html.parser')
    for s in soup.find_all('script', type='application/ld+json'):
        try:
            d = json.loads(s.string)
        except Exception:
            continue
        if isinstance(d, dict) and d.get('@type') not in ('BreadcrumbList', None):
            row['ld_type'] = d.get('@type')
            row['name'] = d.get('name')
            a = d.get('address', {})
            row['street'] = a.get('streetAddress'); row['city'] = a.get('addressLocality'); row['zip'] = a.get('postalCode')
            row['mall'] = d.get('containedIn')
            g = d.get('geo', {})
            row['lat'] = g.get('latitude'); row['lng'] = g.get('longitude')
    t = soup.get_text(' ', strip=True)
    title = soup.title.string if soup.title else ''
    row['title'] = (title or '').strip()
    m = re.search(r'Store Features (.*?) (?:Store Hours|New Arrivals)', t)
    row['features'] = m.group(1)[:400] if m else ''
    row['hos'] = int(bool(re.search(r'house of sport', t, re.I)))
    row['fh'] = int(bool(re.search(r'field house', t, re.I)))
    m = re.search(r'(?i)(grand opening[^.]{0,120})', t)
    row['grand_opening'] = m.group(1) if m else ''
    m = re.search(r'(?i)(coming soon[^.]{0,80})', t)
    row['coming_soon'] = m.group(1) if m else ''
    return row


if __name__ == '__main__':
    with ThreadPoolExecutor(4) as ex:
        rows = list(ex.map(parse, locs))
    keys = sorted({k for r in rows for k in r})
    with open(BASE + r'\H05_dks_store_pages.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, keys); w.writeheader(); w.writerows(rows)
    print(len(rows), sum(r.get('hos', 0) for r in rows), sum(r.get('fh', 0) for r in rows))
