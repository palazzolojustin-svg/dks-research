"""L4: Google News + Bing News RSS search. Usage: python L4_newsrss.py "<query>" ["<query2>" ...]
Prints date | source | title | link (Google links are news.google redirect URLs). Appends to raw/L4_newsrss.txt."""
import sys, requests, re, html, time
from bs4 import BeautifulSoup
import warnings; warnings.filterwarnings('ignore')
UA = {'User-Agent': 'Mozilla/5.0 (research; palazzolojustin@gmail.com)'}
out = open(r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\L4_newsrss.txt', 'a', encoding='utf-8')
for q in sys.argv[1:]:
    for eng, url in [('G', 'https://news.google.com/rss/search'), ('B', 'https://www.bing.com/news/search')]:
        p = {'q': q, 'hl': 'en-US', 'gl': 'US', 'ceid': 'US:en'} if eng == 'G' else {'q': q, 'format': 'rss', 'count': 50}
        try:
            r = requests.get(url, params=p, headers=UA, timeout=30)
            soup = BeautifulSoup(r.content, 'xml')
        except Exception as e:
            print('ERR', eng, e); continue
        items = soup.find_all('item')
        hdr = f'\n=== [{eng}] {q} ({len(items)})'; print(hdr); out.write(hdr + '\n')
        for it in items[:40]:
            t = it.title.text if it.title else ''
            d = it.pubDate.text[:16] if it.pubDate else ''
            src = it.source.text if it.source else ''
            link = it.link.text if it.link else ''
            desc = BeautifulSoup(html.unescape(it.description.text), 'html.parser').get_text(' ')[:250] if (eng == 'B' and it.description) else ''
            line = f'{d} | {src} | {t} | {link}' + (f'\n      {desc}' if desc else '')
            print(line); out.write(line + '\n')
        time.sleep(1)
out.close()
