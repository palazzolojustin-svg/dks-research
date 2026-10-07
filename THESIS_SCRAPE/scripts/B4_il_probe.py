"""B4: probe Illinois DOR tax statistics pages for municipal sales by kind of business (SIC/category).
Rerun: python B4_il_probe.py [url ...]"""
import sys, re, requests
H = {'User-Agent': 'Mozilla/5.0 research palazzolojustin@gmail.com'}
urls = sys.argv[1:] or ['https://tax.illinois.gov/research/taxstats.html']
for u in urls:
    try:
        r = requests.get(u, headers=H, timeout=40)
    except Exception as e:
        print(u, 'ERR', e); continue
    print(u, r.status_code, len(r.text))
    for href, txt in re.findall(r'href="([^"]+)"[^>]*>([^<]{3,90})<', r.text):
        s = (href + ' ' + txt).lower()
        if any(k in s for k in ['sic', 'kind', 'municip', 'category', 'standard industrial', 'quarterly', 'sales tax']):
            print('  ', txt.strip()[:80], '|', href[:150])
