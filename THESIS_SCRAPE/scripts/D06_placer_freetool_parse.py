"""D06: parse Placer.ai free-tools chain pages (public HTML) for visible metrics (YoY change, rank, period text).
Usage: python THESIS_SCRAPE/scripts/D06_placer_freetool_parse.py <chain-slug> [...]
e.g. dicks-sporting-goods academy-sports-outdoors scheels foot-locker
Saves HTML to raw/D06_placer_freetool_<slug>.html and prints text around the metrics block.
"""
import sys, os, re, requests
from bs4 import BeautifulSoup as B
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36'}
for slug in sys.argv[1:]:
    u = f'https://www.placer.ai/free-tools/chains/{slug}'
    r = requests.get(u, headers=H, timeout=60)
    t = r.text
    open(os.path.join(BASE, 'raw', f'D06_placer_freetool_{slug}.html'), 'w', encoding='utf-8').write(t)
    print('=====', slug, r.status_code)
    vals = re.findall(r'data-value="([^"]*)"', t)
    print('data-values:', vals)
    i = t.find('Nationwide Foot Traffic')
    j = t.find('Most Visited')
    for k in (i, j):
        if k > 0:
            print(B(t[max(0, k - 4000):k + 6000], 'html.parser').get_text(' | ', strip=True)[:3000])
            print('--')
