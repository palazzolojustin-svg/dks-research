"""B6 wave 3: find Industry Dive (Retail Dive / CX Dive / Supply Chain Dive) article URLs via their search pages, then fetch.
Rerun: python B6_w3_dive.py
"""
import requests, re, sys
H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/127.0 Safari/537.36'}
SEARCH = [
    ('https://www.customerexperiencedive.com', "dick's sporting goods"),
    ('https://www.retaildive.com', "dick's sporting goods AI"),
    ('https://www.retaildive.com', "retail executives AI"),
    ('https://www.supplychaindive.com', "dick's sporting goods"),
    ('https://www.retaildive.com', "dick's sporting goods store teammates"),
]
for base, q in SEARCH:
    try:
        r = requests.get(base + '/search/', params={'q': q}, headers=H, timeout=40)
    except Exception as e:
        print('ERR', base, e); continue
    print('==', base, q, r.status_code)
    for m in sorted(set(re.findall(r'href=\"([^\"]*/news/[^\"]+)\"', r.text))):
        if re.search(r'dick|ai-|executives|labor|store', m, re.I):
            print('  ', base + m)
