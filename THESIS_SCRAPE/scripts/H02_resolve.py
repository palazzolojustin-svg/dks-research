"""H02: resolve Google-News headlines to original article URLs (via Bing RSS title search), then fetch
article text and print keyword windows. Input: a text file, one headline per line ("title - Source").
Rerun: python H02_resolve.py titles.txt out.json [kw1,kw2,...]
"""
import sys, re, json, time
from H02_search import bing_rss
from H02_fetch_text import text_of


def words(s):
    return set(w for w in re.findall(r'[a-z0-9]+', s.lower()) if len(w) > 2)


titles = [l.strip() for l in open(sys.argv[1], encoding='utf8') if l.strip()]
kws = sys.argv[3].split(',') if len(sys.argv) > 3 else ['open', '2027', '2026', 'square', 'sq', 'relocat', 'close']
out = {}
for t in titles:
    head = t.rsplit(' - ', 1)[0]
    best = None
    try:
        res = bing_rss(head, 10) or []
        tw = words(head)
        scored = sorted(res, key=lambda r: -len(tw & words(r[0])))
        if scored and len(tw & words(scored[0][0])) >= max(2, len(tw) // 2):
            best = scored[0][1]
    except Exception as e:
        pass
    rec = {'title': t, 'url': best}
    if best:
        try:
            code, meta, txt = text_of(best)
            rec['code'] = code; rec['meta'] = meta
            snips = []
            for k in kws:
                for m in re.finditer(re.escape(k), txt, re.I):
                    snips.append(txt[max(0, m.start() - 250): m.start() + 300])
                    if len(snips) > 12:
                        break
            rec['snips'] = snips[:12]
        except Exception as e:
            rec['err'] = str(e)
    out[t] = rec
    print('##', t, '->', best, flush=True)
    for s in rec.get('snips', [])[:6]:
        print('   ..', s.replace('\n', ' ')[:550])
    time.sleep(1)
json.dump(out, open(sys.argv[2], 'w', encoding='utf8'), indent=1)
