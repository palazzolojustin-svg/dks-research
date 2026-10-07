"""H07: classify every DKS-family store page from stores.dickssportinggoods.com sitemap by banner
(House of Sport / Field House / DICK'S / Golf Galaxy etc.) and capture address.
Rerun: python H07_store_classify.py  -> writes THESIS_SCRAPE/raw/H07_store_list.csv
"""
import requests, re, csv, time, html
from concurrent.futures import ThreadPoolExecutor
H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}
OUT = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\H07_store_list.csv'
s = requests.get('https://stores.dickssportinggoods.com/sitemap.xml', headers=H).text
locs = [l for l in re.findall(r'<loc>(.*?)</loc>', s) if re.search(r'/\d+/$', l)]
print(len(locs))

def get(u):
    for a in range(3):
        try:
            r = requests.get(u, headers=H, timeout=30)
            t = r.text
            names = re.findall(r"(DICK&#x27;S[^<\"#]{0,60}#\d+[^<\"]{0,60})", t)
            title = re.search(r'<title>(.*?)</title>', t, re.S)
            addr = re.search(r'"streetAddress"\s*:\s*"([^"]*)"', t)
            zipc = re.search(r'"postalCode"\s*:\s*"([^"]*)"', t)
            sid = u.rstrip('/').split('/')[-1]
            nm = [html.unescape(n) for n in names if '#' + sid in n]
            return [u, sid, u.split('/')[3], u.split('/')[4], nm[0] if nm else '', html.unescape(title.group(1).strip()) if title else '',
                    addr.group(1) if addr else '', zipc.group(1) if zipc else '']
        except Exception as e:
            time.sleep(2)
    return [u, '', '', '', 'ERR', '', '', '']

with ThreadPoolExecutor(6) as ex:
    rows = list(ex.map(get, locs))
with open(OUT, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['url', 'store_id', 'state', 'city', 'name', 'title', 'street', 'zip']); w.writerows(rows)
print('done', len(rows))
