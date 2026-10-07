"""B6 wave 3: Wayback CDX first/last capture dates for vendor pages that name DKS (date the RFID source-tagging mandate etc.).
Rerun: python B6_w3_cdx.py [url_pattern ...]
"""
import requests, sys
H = {'User-Agent': 'DKS research palazzolojustin@gmail.com'}
URLS = sys.argv[1:] or [
    'checkpointsystems.com/general-merchandise-rfid-portal/starting-rfid-project/dicks-sporting-good-compliant/',
    'checkpointsystems.com/*dicks*',
    'rfid.auburn.edu/*',
    'averydennison.com/*dicks*',
    'rbis.averydennison.com/*dick*',
]
for u in URLS:
    try:
        r = requests.get('http://web.archive.org/cdx/search/cdx', params={'url': u, 'output': 'txt', 'limit': 2000, 'fl': 'timestamp,original,statuscode', 'collapse': 'urlkey' if '*' in u else 'digest'}, headers=H, timeout=90)
        lines = [l for l in r.text.splitlines() if l.strip()]
        print('==', u, len(lines))
        for l in lines[:40]:
            if '*' not in u or 'dick' in l.lower() or 'retailer' in l.lower():
                print('  ', l)
    except Exception as e:
        print('ERR', u, e)
