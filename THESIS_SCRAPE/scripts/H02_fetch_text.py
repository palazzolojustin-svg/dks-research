"""H02 helper: fetch a URL with requests and print visible text (optionally filtered by keywords).
Rerun: python H02_fetch_text.py <url> [keyword1,keyword2] [maxchars]
"""
import sys, re, requests
from bs4 import BeautifulSoup

H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0 Safari/537.36',
     'Accept-Language': 'en-US,en;q=0.9'}


def text_of(url):
    r = requests.get(url, headers=H, timeout=45)
    s = BeautifulSoup(r.text, 'html.parser')
    for t in s(['script', 'style', 'noscript']):
        t.decompose()
    meta = []
    for m in s.find_all('meta'):
        if m.get('property') in ('article:published_time', 'og:title') or m.get('name') in ('date', 'pubdate', 'parsely-pub-date'):
            meta.append(f"{m.get('property') or m.get('name')}={m.get('content')}")
    return r.status_code, meta, re.sub(r'\s+', ' ', s.get_text(' '))


if __name__ == '__main__':
    url = sys.argv[1]
    kws = sys.argv[2].split(',') if len(sys.argv) > 2 and sys.argv[2] else []
    mx = int(sys.argv[3]) if len(sys.argv) > 3 else 6000
    code, meta, t = text_of(url)
    print(code, meta)
    times = re.findall(r'(?:Published|Updated|Posted)[^.]{0,60}?20\d\d', t)[:3]
    print('TIMES', times)
    if kws:
        out = []
        for k in kws:
            for m in re.finditer(re.escape(k), t, re.I):
                out.append(t[max(0, m.start() - 400): m.start() + 600])
        print('\n---\n'.join(out)[:mx])
    else:
        print(t[:mx])
