"""B1: resolve Google News links (via H02 decoder) or fetch direct URLs; save text to raw/B1_web/<n>.txt and print keyword windows.
Rerun: python B1_article.py "<title substring>" [kw1,kw2,...]   (looks up the link in raw/B1_search.jsonl)
   or: python B1_article.py URL [kws]
"""
import sys, json, re, os, time, hashlib
sys.path.insert(0, os.path.dirname(__file__))
from H02_gdecode import decode
from H02_fetch_text import text_of
RAW = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw'
os.makedirs(os.path.join(RAW, 'B1_web'), exist_ok=True)
arg = sys.argv[1]
kws = sys.argv[2].split(',') if len(sys.argv) > 2 else ['visit', 'traffic', 'sales', 'million', 'jobs', 'employ', 'square', 'trip', 'tax']
if arg.startswith('http') and 'news.google.com' not in arg:
    url, title = arg, arg
else:
    link = arg
    title = arg
    if not arg.startswith('http'):
        for l in open(os.path.join(RAW, 'B1_search.jsonl'), encoding='utf-8'):
            d = json.loads(l)
            if arg.lower() in d['title'].lower():
                link, title = d['link'], d['title']; break
    url = None
    if 'news.google.com' in link:
        for a in range(3):
            try:
                url = decode(link)
            except Exception:
                url = None
            if url: break
            time.sleep(5 * (a + 1))
    else:
        url = link
print('URL', url)
if not url:
    sys.exit()
code, meta, t = text_of(url)
fn = os.path.join(RAW, 'B1_web', hashlib.md5(url.encode()).hexdigest()[:10] + '.txt')
open(fn, 'w', encoding='utf-8').write(f'{title}\n{url}\n{code} {meta}\n\n{t}')
print(code, meta, 'saved', fn, 'len', len(t))
seen = set()
for k in kws:
    for m in re.finditer(re.escape(k), t, re.I):
        s = max(0, m.start() - 300)
        if any(abs(s - x) < 300 for x in seen): continue
        seen.add(s)
        print('..', t[s: m.start() + 400])
