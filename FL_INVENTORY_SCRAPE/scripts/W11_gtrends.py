"""W11 Google Trends client (public JSON endpoints used by trends.google.com explore page).
Usage: python3 W11_gtrends.py <name> "t1|t2|..." "<timeframe>" <geo> [cat] [gprop]
Writes FL_INVENTORY_SCRAPE/raw/W11/gt_<name>.csv. Values 0-100 relative within the batch; '<1' -> 0.5.
Adapted from PB_SCRAPE/scripts/X09_gtrends.py; uses curl_cffi chrome impersonation if available.
"""
import json, sys, time, os
import pandas as pd
try:
    from curl_cffi import requests as creq
    def sess():
        return creq.Session(impersonate="chrome")
except Exception:
    import requests as creq
    def sess():
        return creq.Session()
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'raw', 'W11')
os.makedirs(RAW, exist_ok=True)
def _j(t): return json.loads(t[t.index('{'):])
_S = None
def S():
    global _S
    if _S is None:
        _S = sess()
        try: _S.get('https://trends.google.com/trends/explore?geo=US', timeout=30)
        except Exception as e: print('warm fail', e, file=sys.stderr)
    return _S
def fetch(terms, timeframe, geo='US', cat=0, gprop='', tries=4):
    global _S
    req = {'comparisonItem': [{'keyword': t, 'geo': geo, 'time': timeframe} for t in terms], 'category': cat, 'property': gprop}
    for a in range(tries):
        try:
            s = S()
            r = s.get('https://trends.google.com/trends/api/explore', params={'hl': 'en-US', 'tz': 300, 'req': json.dumps(req)}, timeout=30)
            if r.status_code != 200: raise RuntimeError(f'{r.status_code} explore')
            w = [x for x in _j(r.text)['widgets'] if x['id'] == 'TIMESERIES'][0]
            r2 = s.get('https://trends.google.com/trends/api/widgetdata/multiline', params={'hl': 'en-US', 'tz': 300, 'req': json.dumps(w['request']), 'token': w['token']}, timeout=30)
            if r2.status_code != 200: raise RuntimeError(f'{r2.status_code} multiline')
            tl = _j(r2.text)['default']['timelineData']
            rows = []
            for p in tl:
                vals = [0.5 if fv == '<1' else float(fv) for fv in p['formattedValue']]
                rows.append([pd.Timestamp(int(p['time']), unit='s').date()] + vals)
            return pd.DataFrame(rows, columns=['date'] + list(terms)).set_index('date')
        except Exception as e:
            print('retry', a, str(e)[:100], file=sys.stderr)
            time.sleep(45 * (a + 1)); _S = None
    raise RuntimeError('failed ' + str(terms))
if __name__ == '__main__':
    name, terms, tf, geo = sys.argv[1], sys.argv[2].split('|'), sys.argv[3], sys.argv[4]
    cat = int(sys.argv[5]) if len(sys.argv) > 5 else 0
    gprop = sys.argv[6] if len(sys.argv) > 6 else ''
    out = os.path.join(RAW, f'gt_{name}.csv')
    df = fetch(terms, tf, geo, cat, gprop)
    df.to_csv(out); print(out); print(df.tail(10).to_string())
