"""H01: probe Town of Braintree (CivicPlus) DocumentCenter IDs near the 250 Granite Street HoS exhibit (16388)
to find sibling filings (traffic study, petition, decision). Prints filename from Content-Disposition.
Rerun: python H01_braintree_docs.py START END
"""
import requests, sys, time, re
H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'}
a, b = int(sys.argv[1]), int(sys.argv[2])
for i in range(a, b + 1):
    u = f'https://braintreema.gov/DocumentCenter/View/{i}'
    try:
        r = requests.get(u, headers=H, timeout=40, stream=True, allow_redirects=True)
        cd = r.headers.get('content-disposition', '')
        fn = re.findall(r'filename\*?=(?:UTF-8\'\')?"?([^";]+)', cd)
        print(i, r.status_code, r.headers.get('content-type', '')[:30], r.headers.get('content-length'), fn[0] if fn else r.url[-80:], flush=True)
        r.close()
    except Exception as e:
        print(i, 'ERR', e)
    time.sleep(0.7)
