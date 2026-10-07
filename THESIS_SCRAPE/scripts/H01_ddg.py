"""H01: simple web search via DuckDuckGo HTML endpoint (WebSearch budget + Apify limit exhausted).
Stops immediately if a challenge/CAPTCHA page is returned (no bypassing).
Rerun: python H01_ddg.py "query1" "query2" ...   -> appends to raw/H01_ddg_results.jsonl
"""
import requests, sys, json, os, time, re
from bs4 import BeautifulSoup
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTF = os.path.join(BASE, 'raw', 'H01_ddg_results.jsonl')
H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'}
for q in sys.argv[1:]:
    r = requests.post('https://html.duckduckgo.com/html/', data={'q': q}, headers=H, timeout=40)
    if r.status_code != 200 or re.search(r'captcha|anomaly|challenge', r.text[:5000], re.I):
        print('BLOCKED/CHALLENGE', r.status_code, q); break
    s = BeautifulSoup(r.text, 'html.parser')
    res = []
    for a in s.select('.result'):
        t = a.select_one('.result__a'); sn = a.select_one('.result__snippet')
        if t:
            res.append({'title': t.get_text(' ', strip=True), 'url': t.get('href'), 'snippet': sn.get_text(' ', strip=True) if sn else ''})
    with open(OUTF, 'a', encoding='utf-8') as f:
        f.write(json.dumps({'q': q, 'res': res}) + '\n')
    print('#####', q, len(res))
    for x in res[:10]:
        print('  -', x['title'][:90], '|', x['url'][:150], '|', x['snippet'][:250])
    time.sleep(4)
