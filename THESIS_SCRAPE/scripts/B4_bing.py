"""B4: Bing News RSS sweep (direct publisher links) for DICK'S Field House / next-gen / relocation openings.
Rerun: python B4_bing.py <queries.txt> <out.json>   (appends; skips queries already in out.json)
"""
import sys, re, json, time, html, requests
from urllib.parse import quote, urlparse, parse_qs

H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0 Safari/537.36'}


def bing(q):
    u = 'https://www.bing.com/news/search?q=' + quote(q) + '&format=rss&count=100'
    r = requests.get(u, headers=H, timeout=25)
    items = []
    for it in re.findall(r'<item>(.*?)</item>', r.text, re.S):
        g = lambda t: html.unescape((re.search(f'<{t}[^>]*>(.*?)</{t}>', it, re.S) or [None, ''])[1])
        link = g('link')
        try:
            link = parse_qs(urlparse(link).query).get('url', [link])[0]
        except Exception:
            pass
        items.append({'title': g('title'), 'link': link, 'date': g('pubDate'), 'desc': g('description')[:400]})
    return r.status_code, items


if __name__ == '__main__':
    qs = [l.strip() for l in open(sys.argv[1], encoding='utf8') if l.strip() and not l.startswith('#')]
    try:
        out = json.load(open(sys.argv[2], encoding='utf8'))
    except Exception:
        out = {}
    for q in qs:
        if out.get(q):
            continue
        try:
            code, items = bing(q)
        except Exception as e:
            code, items = str(e)[:60], []
        out[q] = items
        print('##', q, code, len(items), flush=True)
        json.dump(out, open(sys.argv[2], 'w', encoding='utf8'), indent=1)
        time.sleep(1.0)
    seen = {}
    for q, its in out.items():
        for i in its:
            seen.setdefault(i['link'], i)
    print('unique', len(seen))
