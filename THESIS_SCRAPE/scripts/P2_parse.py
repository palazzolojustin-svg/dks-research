"""P2_parse.py: fetch a Wayback snapshot of a dickssportinggoods.com product page and extract SKU-level prices.
Usage as module: from P2_parse import fetch_prices; fetch_prices(timestamp, original_url) -> dict
CLI test: python P2_parse.py <timestamp> <original_url>
Extracted per variant (catentryId): offerPrice, listPrice, mapPrice, dealsPercentage, clearance flag, name, parentPartNumber.
Raw HTML is cached gzip-compressed in THESIS_SCRAPE\\raw\\P2_html\\ so reruns do not re-download.
"""
import requests, re, json, os, gzip, hashlib, time, sys
H = {'User-Agent': 'DKS price research (palazzolojustin@gmail.com)'}
CACHE = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\P2_html'
os.makedirs(CACHE, exist_ok=True)

PRICE_RE = re.compile(r'"catentryId":(\d+),"parentCatentryId":(\d+).{0,400}?"clearance":(true|false),"prices":\{([^}]*)\},"name":"((?:[^"\\]|\\.)*)"', re.S)
PRICE_RE2 = re.compile(r'"prices":\{([^}]*)\}')


def get_html(ts, url):
    key = hashlib.md5((ts + url).encode()).hexdigest()
    fp = os.path.join(CACHE, key + '.html.gz')
    if os.path.exists(fp):
        with gzip.open(fp, 'rt', encoding='utf-8') as f:
            return f.read()
    wb = 'http://web.archive.org/web/%sid_/%s' % (ts, url)
    last = None
    for attempt in range(4):
        try:
            r = requests.get(wb, headers=H, timeout=180)
            if r.status_code == 200:
                t = r.text
                with gzip.open(fp, 'wt', encoding='utf-8') as f:
                    f.write(t)
                return t
            last = r.status_code
            if r.status_code in (429, 503):
                time.sleep(60 * (attempt + 1))
            else:
                time.sleep(5)
        except Exception as e:
            last = str(e)
            time.sleep(20 * (attempt + 1))
    raise RuntimeError('fetch failed %s %s' % (last, wb))


def parse(t):
    out = {}
    for m in PRICE_RE.finditer(t):
        cid, pcid, clr, pr, name = m.groups()
        d = {}
        for kv in pr.split(','):
            if ':' in kv:
                k, v = kv.split(':', 1)
                try:
                    d[k.strip('"')] = float(v)
                except ValueError:
                    d[k.strip('"')] = v
        # part number
        seg = t[max(0, m.start() - 300):m.start()]
        pn = re.findall(r'"parentPartNumber":"([^"]+)"', seg)
        out[cid] = dict(catentry=cid, parent=pcid, clearance=(clr == 'true'), name=name, parentPartNumber=(pn[-1] if pn else ''),
                        offer=d.get('offerPrice'), list=d.get('listPrice'), map=d.get('mapPrice'), deals=d.get('dealsPercentage'),
                        priceIndicator=d.get('priceIndicator'), mapInd=d.get('mapPriceIndicator'))
    return out


def fetch_prices(ts, url):
    t = get_html(ts, url)
    v = parse(t)
    meta = {'len': len(t), 'n_prices_blocks': len(PRICE_RE2.findall(t))}
    title = re.search(r'<title>(.*?)</title>', t, re.S)
    meta['title'] = title.group(1).strip()[:150] if title else ''
    return v, meta


if __name__ == '__main__':
    v, meta = fetch_prices(sys.argv[1], sys.argv[2])
    print(meta)
    for k, x in list(v.items())[:10]:
        print(x)
    print(len(v))
