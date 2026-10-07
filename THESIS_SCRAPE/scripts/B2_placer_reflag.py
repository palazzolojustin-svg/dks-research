"""B2: re-fetch Placer articles harvested before precise flags were added (records without 'flags' in
raw/B2_placer_embeds.jsonl) and write precise DICK'S / House of Sport / Foot Locker mention flags + text snippets to
raw/B2_placer_reflag.jsonl (resumable). Rerun: python B2_placer_reflag.py
"""
import json, os, time, sys
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import B2_placer_embeds as E
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INF = os.path.join(BASE, 'raw', 'B2_placer_embeds.jsonl')
OUTF = os.path.join(BASE, 'raw', 'B2_placer_reflag.jsonl')
todo = []
for l in open(INF, encoding='utf-8'):
    r = json.loads(l)
    if 'flags' not in r and not r.get('error'):
        todo.append(r['url'])
done = set()
if os.path.exists(OUTF):
    done = {json.loads(l)['url'] for l in open(OUTF, encoding='utf-8')}
todo = [u for u in todo if u not in done]
print('todo', len(todo), flush=True)


def work(u):
    t = E.get(u)
    time.sleep(2)
    return E.parse(u, t) if t else {'url': u, 'error': 'fetch failed'}


with ThreadPoolExecutor(2) as ex:
    for rec in ex.map(work, todo):
        with open(OUTF, 'a', encoding='utf-8') as f:
            f.write(json.dumps(rec) + '\n')
        fl = rec.get('flags', {})
        if any(fl.values()):
            print('HIT', fl, rec.get('pub', '')[:18], rec['url'].rsplit('/', 1)[-1][:80], len(rec.get('infogram', [])), flush=True)
print('done')
