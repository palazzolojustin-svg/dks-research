"""P2_fetch.py: fetch Wayback snapshots listed in a plan CSV (P2_plan_panel.csv / P2_plan_xsec.csv / P2_plan_basket.csv) and write
variant-level prices to raw\\P2_prices_<planname>.csv. Uses the gzip cache in raw\\P2_html (resumable).
Rerun: python P2_fetch.py ..\\raw\\P2_plan_panel.csv [threads]
"""
import csv, sys, os, time, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from P2_parse import fetch_prices

plan = sys.argv[1]
threads = int(sys.argv[2]) if len(sys.argv) > 2 else 4
name = os.path.basename(plan).replace('P2_plan_', '').replace('.csv', '')
out = os.path.join(os.path.dirname(os.path.abspath(plan)), 'P2_prices_%s.csv' % name)
rows = list(csv.DictReader(open(plan, encoding='utf-8')))
lock = threading.Lock()
fields = list(rows[0].keys()) + ['title', 'html_len', 'catentry', 'partnumber', 'vname', 'clearance', 'list', 'offer', 'map', 'deals', 'priceIndicator', 'mapInd', 'status']
f = open(out, 'w', newline='', encoding='utf-8')
w = csv.DictWriter(f, fieldnames=fields)
w.writeheader()

def job(r):
    try:
        v, meta = fetch_prices(r['timestamp'], r['original'])
        return r, v, meta, 'ok'
    except Exception as e:
        return r, {}, {'title': '', 'len': 0}, 'ERR ' + str(e)[:100]

done = 0
t0 = time.time()
with ThreadPoolExecutor(threads) as ex:
    futs = [ex.submit(job, r) for r in rows]
    for fu in as_completed(futs):
        r, v, meta, st = fu.result()
        with lock:
            base = dict(r); base.update(title=meta.get('title', ''), html_len=meta.get('len', 0), status=st)
            vs = [x for x in v.values() if x.get('list')]
            if not vs:
                w.writerow(base)
            for x in vs:
                d = dict(base)
                d.update(catentry=x['catentry'], partnumber=x['parentPartNumber'], vname=x['name'], clearance=x['clearance'], list=x['list'],
                         offer=x['offer'], map=x['map'], deals=x['deals'], priceIndicator=x['priceIndicator'], mapInd=x['mapInd'])
                w.writerow(d)
            f.flush()
            done += 1
            if done % 25 == 0:
                print(done, len(rows), round(time.time() - t0), flush=True)
f.close()
print('done', out)
