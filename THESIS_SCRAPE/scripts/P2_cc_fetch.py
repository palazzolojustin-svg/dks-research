"""P2_cc_fetch.py: fetch a Common Crawl WARC record (range request on data.commoncrawl.org) and parse DKS product-page prices
(same 'prices' JSON as the Wayback parser). Cache: raw\\P2_html\\cc_<md5>.html.gz
Module: from P2_cc_fetch import cc_prices; cc_prices(filename, offset, length) -> (variants dict, meta)
CLI: python P2_cc_fetch.py <filename> <offset> <length>
"""
import requests, gzip, zlib, os, hashlib, time, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from P2_parse import parse, PRICE_RE2
H = {'User-Agent': 'DKS price research (palazzolojustin@gmail.com)'}
CACHE = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\P2_html'

def cc_html(filename, offset, length):
    offset, length = int(offset), int(length)
    key = hashlib.md5(('%s|%d' % (filename, offset)).encode()).hexdigest()
    fp = os.path.join(CACHE, 'cc_' + key + '.html.gz')
    if os.path.exists(fp):
        with gzip.open(fp, 'rt', encoding='utf-8') as f:
            return f.read()
    url = 'https://data.commoncrawl.org/' + filename
    for a in range(5):
        try:
            r = requests.get(url, headers=dict(H, Range='bytes=%d-%d' % (offset, offset + length - 1)), timeout=120)
            if r.status_code in (200, 206):
                break
        except Exception:
            pass
        time.sleep(5 * (a + 1))
    else:
        raise RuntimeError('fail')
    data = zlib.decompress(r.content, 16 + zlib.MAX_WBITS)
    # split WARC header / HTTP header / body
    parts = data.split(b'\r\n\r\n', 2)
    body = parts[2] if len(parts) > 2 else b''
    t = body.decode('utf-8', 'replace')
    with gzip.open(fp, 'wt', encoding='utf-8') as f:
        f.write(t)
    return t

def cc_prices(filename, offset, length):
    t = cc_html(filename, offset, length)
    v = parse(t)
    title = re.search(r'<title>(.*?)</title>', t, re.S)
    return v, {'len': len(t), 'title': title.group(1).strip()[:150] if title else '', 'n_prices_blocks': len(PRICE_RE2.findall(t))}

if __name__ == '__main__':
    v, m = cc_prices(*sys.argv[1:4])
    print(m)
    for x in list(v.values())[:6]:
        print(x)
