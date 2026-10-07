"""H02: Google News RSS search (public RSS feed, no login). Saves all items for many queries.
Rerun: python H02_gnews.py queries.txt out.json
Each query string is passed as-is (quotes supported). Use 'when:' or 'after:YYYY-MM-DD before:YYYY-MM-DD' operators to slice time.
"""
import sys, re, json, time, html, requests
from urllib.parse import quote

H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0 Safari/537.36'}


def gnews(q):
    u = 'https://news.google.com/rss/search?q=' + quote(q) + '&hl=en-US&gl=US&ceid=US:en'
    r = requests.get(u, headers=H, timeout=30)
    items = []
    for it in re.findall(r'<item>(.*?)</item>', r.text, re.S):
        g = lambda t: html.unescape((re.search(f'<{t}[^>]*>(.*?)</{t}>', it, re.S) or [None, ''])[1])
        items.append({'title': g('title'), 'link': g('link'), 'date': g('pubDate'), 'source': g('source')})
    return r.status_code, items


if __name__ == '__main__':
    qs = [l.strip() for l in open(sys.argv[1], encoding='utf8') if l.strip() and not l.startswith('#')]
    out = {}
    try:
        out = json.load(open(sys.argv[2], encoding='utf8'))
    except Exception:
        pass
    for q in qs:
        if q in out and out[q]:
            continue
        code, items = 0, []
        for a in range(4):
            try:
                code, items = gnews(q); break
            except Exception as e:
                time.sleep(4 + 4 * a)
        out[q] = items
        print('##', q, code, len(items), flush=True)
        time.sleep(1.0)
    json.dump(out, open(sys.argv[2], 'w', encoding='utf8'), indent=1)
    # dedupe all titles
    seen = {}
    for q, its in out.items():
        for i in its:
            seen.setdefault(i['title'], i)
    print('unique', len(seen))
