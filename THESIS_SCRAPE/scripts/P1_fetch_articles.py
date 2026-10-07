"""P1: decode Google News / Bing News RSS links from raw/P1_newsrss.csv for titles matching substrings, fetch article text,
save to raw/P1_articles/<n>.txt and print keyword windows.
Rerun: python P1_fetch_articles.py "title substring 1" "title substring 2" ...   (kw windows: price, %, $)
"""
import sys, os, re, csv, time, requests
from urllib.parse import urlparse, parse_qs, unquote
sys.path.insert(0, os.path.dirname(__file__))
from H02_gdecode import decode
from H02_fetch_text import text_of
BASE = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw'
OUTD = os.path.join(BASE, 'P1_articles'); os.makedirs(OUTD, exist_ok=True)
KW = ['price', 'pric', 'tariff', 'MSRP', '%', '$']


def resolve(link):
    if 'bing.com/news/apiclick' in link:
        return unquote(parse_qs(urlparse(link).query)['url'][0])
    if 'news.google.com' in link:
        for a in range(3):
            try:
                u = decode(link)
                if u:
                    return u
            except Exception:
                pass
            time.sleep(5 * (a + 1))
        return None
    return link


if __name__ == '__main__':
    rows = list(csv.reader(open(os.path.join(BASE, 'P1_newsrss.csv'), encoding='utf-8')))
    for s in sys.argv[1:]:
        hits = [r for r in rows if len(r) > 4 and s.lower() in r[3].lower()]
        if not hits:
            print('## NOHIT', s); continue
        r = hits[0]
        url = resolve(r[4])
        print('##', r[3][:100], '|', r[2][:16], '->', url, flush=True)
        if not url:
            continue
        try:
            code, meta, txt = text_of(url)
        except Exception as e:
            print('  ERR', e); continue
        fn = os.path.join(OUTD, re.sub(r'[^A-Za-z0-9]+', '_', s)[:60] + '.txt')
        open(fn, 'w', encoding='utf-8').write(f'TITLE: {r[3]}\nDATE: {r[2]}\nURL: {url}\nCODE: {code}\n\n{txt}')
        print('  code', code, 'len', len(txt), '->', fn)
        time.sleep(1)
