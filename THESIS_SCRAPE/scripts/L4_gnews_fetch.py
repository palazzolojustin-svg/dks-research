"""L4: Google News RSS query -> pick items whose title matches a regex -> decode GN link (H02_gdecode.decode)
-> fetch article text (H02_fetch_text.text_of) -> print keyword windows. Appends to raw/L4_gnews_articles.txt
Usage: python L4_gnews_fetch.py "<query>" "<title regex>" "<kw regex>" [max_articles]
"""
import sys, re, time, requests, html
from bs4 import BeautifulSoup
import warnings; warnings.filterwarnings('ignore')
sys.path.insert(0, r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\scripts')
from H02_gdecode import decode
from H02_fetch_text import text_of
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0 Safari/537.36'}
q, trx, krx = sys.argv[1], sys.argv[2], sys.argv[3]
mx = int(sys.argv[4]) if len(sys.argv) > 4 else 4
out = open(r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\L4_gnews_articles.txt', 'a', encoding='utf-8')
items = []
for a in range(3):
    try:
        r = requests.get('https://news.google.com/rss/search', params={'q': q, 'hl': 'en-US', 'gl': 'US', 'ceid': 'US:en'}, headers=UA, timeout=30)
        items = BeautifulSoup(r.content, 'xml').find_all('item'); break
    except Exception as e:
        print('rss retry', e); time.sleep(5 * (a + 1))
print(f'=== {q}: {len(items)} items')
n = 0
for it in items:
    t = it.title.text
    if not re.search(trx, t, re.I):
        continue
    d = it.pubDate.text[:16] if it.pubDate else ''
    url = None
    for a in range(3):
        try:
            url = decode(it.link.text)
        except Exception:
            url = None
        if url: break
        time.sleep(5 * (a + 1))
    hdr = f'\n##### {d} | {t} | {url}'
    print(hdr); out.write(hdr + '\n')
    if url:
        try:
            code, meta, txt = text_of(url)
            last = -999
            for m in re.finditer(krx, txt, re.I):
                if m.start() - last < 400: continue
                last = m.start()
                s = '   .. ' + txt[max(0, m.start() - 350): m.start() + 450].replace('\n', ' ')
                print(s); out.write(s + '\n')
            print('   [len', len(txt), 'code', code, ']')
        except Exception as e:
            print('   ERR', str(e)[:150])
    n += 1
    if n >= mx: break
    time.sleep(1.5)
out.close()
