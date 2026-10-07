"""H02: decode Google News RSS article links to publisher URLs (public batchexecute flow the GN page itself uses),
then fetch article text and print keyword windows.
Rerun: python H02_gdecode.py <title-substring-file> <gnews.json> <out.json> [kw1,kw2]
"""
import sys, re, json, time, requests
from urllib.parse import urlparse, quote
from H02_fetch_text import text_of

H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0 Safari/537.36'}


def decode(link):
    gid = urlparse(link).path.split('/')[-1]
    r = requests.get(f'https://news.google.com/rss/articles/{gid}', headers=H, timeout=30)
    sg = re.search(r'data-n-a-sg="([^"]+)"', r.text)
    ts = re.search(r'data-n-a-ts="([^"]+)"', r.text)
    if not sg or not ts:
        return None
    payload = ['Fbv4je', f'["garturlreq",[["X","X",["X","X"],null,null,1,1,"US:en",null,1,null,null,null,null,null,0,1],"X","X",1,[1,1,1],1,1,null,0,0,null,0],"{gid}",{ts.group(1)},"{sg.group(1)}"]']
    req = 'f.req=' + quote(json.dumps([[payload]]))
    r2 = requests.post('https://news.google.com/_/DotsSplashUi/data/batchexecute', data=req,
                       headers={**H, 'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'}, timeout=30)
    try:
        body = json.loads(r2.text.split('\n\n')[1])
        return json.loads(body[0][2])[1]
    except Exception:
        m = re.search(r'https?://[^"\\]+', r2.text.split('garturlres')[-1]) if 'garturlres' in r2.text else None
        return m.group(0) if m else None


if __name__ == '__main__':
    subs = [l.strip() for l in open(sys.argv[1], encoding='utf8') if l.strip()]
    g = json.load(open(sys.argv[2], encoding='utf8'))
    allit = {}
    for its in g.values():
        for i in its:
            allit.setdefault(i['title'], i)
    kws = sys.argv[4].split(',') if len(sys.argv) > 4 else ['open', '2027', '2026', 'square']
    out = {}
    for s in subs:
        hits = [i for t, i in allit.items() if s.lower() in t.lower()]
        if not hits:
            print('## NOHIT', s); continue
        it = hits[0]
        url = None
        for a in range(3):
            try:
                url = decode(it['link'])
            except Exception as e:
                url = None
            if url:
                break
            time.sleep(6 * (a + 1))
        rec = {'title': it['title'], 'date': it['date'], 'url': url}
        if url:
            try:
                code, meta, txt = text_of(url)
                rec['code'] = code; rec['meta'] = meta
                snips = []
                for k in kws:
                    for m in re.finditer(re.escape(k), txt, re.I):
                        snips.append(txt[max(0, m.start() - 250): m.start() + 300])
                rec['snips'] = snips[:14]
                rec['len'] = len(txt)
            except Exception as e:
                rec['err'] = str(e)[:200]
        out[s] = rec
        print('##', it['title'], '|', it['date'][:16], '->', url, rec.get('code'), flush=True)
        for sn in rec.get('snips', [])[:7]:
            print('   ..', sn[:550])
        time.sleep(1)
    json.dump(out, open(sys.argv[3], 'w', encoding='utf8'), indent=1)
