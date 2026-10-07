"""B2: harvest chart embeds (Infogram data-ids, Datawrapper ids, Placer editorial widgets) from Placer.ai Anchor articles.
Step 1 of the 'Placer chart data' pipeline (step 2 = B2_infogram.py fetches the data behind each Infogram id).
Filters articles by slug keyword (sporting goods / DICK'S / malls / retail indices / footwear / holidays) unless ALL=1.
Resumable: skips URLs already in raw/B2_placer_embeds.jsonl.
Rerun: python B2_placer_embeds.py [ALL]
"""
import requests, re, time, os, sys, json, html
from concurrent.futures import ThreadPoolExecutor
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTF = os.path.join(BASE, 'raw', 'B2_placer_embeds.jsonl')
H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'}
KW = re.compile(r"dick|sport|athlet|foot-?locker|sneaker|footwear|shoe|mall|back-to-school|bts|holiday|black-friday|retail-(and-dining-)?index|"
                r"academy|nike|adidas|golf|lululemon|hibbett|scheels|apparel|experiential|super-bowl|world-cup|thanksgiving|"
                r"christmas|memorial|labor-day|tax-free|year-in-review|anchor|outdoor|fitness|kids|q[1-4]-20|h[12]-20|20(25|26)", re.I)
ALL = len(sys.argv) > 1 and sys.argv[1].upper() == 'ALL'


def get(u):
    for i in range(4):
        try:
            r = requests.get(u, headers=H, timeout=60)
            if r.status_code == 200:
                return r.text
            if r.status_code in (403, 429):
                time.sleep(20 * (i + 1))
                continue
            return ''
        except Exception:
            time.sleep(8 * (i + 1))
    return None


def parse(u, t):
    pub = ''
    m = re.search(r'"datePublished"\s*:\s*"([^"]+)"', t)
    if m:
        pub = m.group(1)
    if not pub:
        m = re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, 20\d\d', t)
        pub = m.group(0) if m else ''
    title = ''
    m = re.search(r'<title>([^<]*)</title>', t)
    if m:
        title = html.unescape(m.group(1))
    info = [(a, html.unescape(html.unescape(b))) for a, b in re.findall(r'class="infogram-embed"\s+data-id="([^"]+)"[^>]*?data-title="([^"]*)"', t)]
    info += [(a, '') for a in re.findall(r'data-id="(_/[^"]+)"', t) if a not in [x[0] for x in info]]
    dw = sorted(set(re.findall(r'datawrapper\.dwcdn\.net/([A-Za-z0-9]{5})/', t)))
    wid = sorted(set(html.unescape(x) for x in re.findall(r'(https://embedded-widget\.placer\.ai/widgets/v1/editorial/\?[^"\'<>\s]+)', t)))
    body_has = bool(re.search(r"DICK.?S|House of Sport|Field House|Foot Locker", t[t.find('post-body'):t.find('post-body') + 120000] if 'post-body' in t else t, re.I))
    # precise flags from visible key-takeaway + post-body text only
    try:
        from bs4 import BeautifulSoup
        s = BeautifulSoup(t, 'html.parser')
        txt = ' '.join(el.get_text(' ', strip=True) for c in ['key-takeaway-richtext', 'post-body'] for el in s.find_all(class_=c))
        txt += ' ' + ' '.join(b for _, b in info)
    except Exception:
        txt = ''
    flags = {'hos': bool(re.search(r'House of Sport', txt, re.I)), 'dks': bool(re.search(r"DICK.?S Sporting|DICK.?S\b", txt)),
             'fl': bool(re.search(r'Foot Locker|Champs Sports', txt, re.I))}
    snips = [txt[max(0, m.start() - 250): m.end() + 350] for m in re.finditer(r"House of Sport|DICK.?S|Foot Locker", txt)][:6]
    return {'url': u, 'pub': pub, 'title': title, 'infogram': info, 'datawrapper': dw, 'widgets': wid, 'mentions_dks_fl': body_has,
            'flags': flags, 'snips': snips}


def main():
    sm = get('https://www.placer.ai/sitemap.xml') or ''
    items = re.findall(r'<loc>(https://www\.placer\.ai/anchor/(?:articles|reports)/[^<]+)</loc>(?:\s*<lastmod>([^<]+)</lastmod>)?', sm)
    print('sitemap anchor items', len(items))
    urls = [u for u, d in items if ALL or KW.search(u.rsplit('/', 1)[-1])]
    done = set()
    if os.path.exists(OUTF):
        for l in open(OUTF, encoding='utf-8'):
            try:
                done.add(json.loads(l)['url'])
            except Exception:
                pass
    todo = [u for u in urls if u not in done]
    print('selected', len(urls), 'todo', len(todo))

    def work(u):
        t = get(u)
        time.sleep(1.5)
        if not t:
            return {'url': u, 'error': 'fetch failed'}
        return parse(u, t)

    with ThreadPoolExecutor(3) as ex:
        for rec in ex.map(work, todo):
            with open(OUTF, 'a', encoding='utf-8') as f:
                f.write(json.dumps(rec) + '\n')
            fl = rec.get('flags', {})
            if any(fl.values()):
                print('HIT', fl, rec.get('pub', '')[:18], rec['url'].rsplit('/', 1)[-1][:80], len(rec.get('infogram', [])), flush=True)
    print('done')


if __name__ == '__main__':
    main()
