"""H02 helper: web search via Bing RSS feed (format=rss) or DuckDuckGo HTML endpoint, no JS, no login.
Rerun: python H02_search.py "query" [n]
Prints title | url | date | snippet. If blocked (captcha/non-200) it prints BLOCKED and does not retry.
"""
import sys, re, html, requests
from bs4 import BeautifulSoup

H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0 Safari/537.36',
     'Accept-Language': 'en-US,en;q=0.9'}


def bing_rss(q, n=20):
    r = requests.get('https://www.bing.com/search', params={'q': q, 'format': 'rss', 'count': n}, headers=H, timeout=30)
    if r.status_code != 200 or '<rss' not in r.text[:500]:
        return None
    out = []
    for it in re.findall(r'<item>(.*?)</item>', r.text, re.S):
        g = lambda t: html.unescape((re.search(f'<{t}>(.*?)</{t}>', it, re.S) or [None, ''])[1])
        out.append((g('title'), g('link'), g('pubDate'), g('description')))
    return out


def ddg(q):
    r = requests.post('https://html.duckduckgo.com/html/', data={'q': q}, headers=H, timeout=30)
    if r.status_code != 200:
        return None
    s = BeautifulSoup(r.text, 'html.parser')
    out = []
    for a in s.select('.result'):
        t = a.select_one('.result__a'); sn = a.select_one('.result__snippet')
        if t:
            out.append((t.get_text(' ', strip=True), t.get('href'), '', sn.get_text(' ', strip=True) if sn else ''))
    return out


if __name__ == '__main__':
    q = sys.argv[1]
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    res = bing_rss(q, n)
    src = 'bing'
    if not res:
        res = ddg(q); src = 'ddg'
    if not res:
        print('BLOCKED/EMPTY'); sys.exit()
    for t, u, d, s in res:
        print(f'[{src}] {t} | {u} | {d} | {s[:300]}')
