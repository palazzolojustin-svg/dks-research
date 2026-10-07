"""X09 Google Trends puller (DKS owned-brand search demand).

Rerun:  python X09_gtrends.py <batch_name> "<term1>|<term2>|..." [timeframe] [geo] [category]
  e.g.  python X09_gtrends.py core "calia|vrst|maxfli|lululemon|vuori" "2021-01-01 2026-10-06" US 0
Writes PB_SCRAPE/raw/X09_gt_<batch_name>.csv  (columns = terms, index = period start, values 0-100
relative within the batch; '<1' -> 0.5).

Method: hits the same public JSON endpoints the trends.google.com explore page calls
(/trends/api/explore -> widget token -> /trends/api/widgetdata/multiline). No login, no captcha.
Max 5 terms per batch; keep one ANCHOR term in every batch to chain batches together.
Be polite: sleep >= 20-60 s between batches; on 429 back off several minutes.
A term can be a Topic entity id (e.g. '/m/0abc12') instead of a text string.
"""
import json, sys, time, os
import requests
import pandas as pd

RAW = os.path.join(os.path.dirname(__file__), '..', 'raw')
H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/129.0 Safari/537.36', 'Accept-Language': 'en-US,en;q=0.9'}


def _j(txt):
    return json.loads(txt[txt.index('{'):])


def fetch(terms, timeframe='2021-01-01 2026-10-06', geo='US', cat=0, gprop='', session=None, tries=6):
    s = session or requests.Session()
    req = {'comparisonItem': [{'keyword': t, 'geo': geo, 'time': timeframe} for t in terms],
           'category': cat, 'property': gprop}
    for a in range(tries):
        try:
            r = s.get('https://trends.google.com/trends/api/explore',
                      params={'hl': 'en-US', 'tz': 300, 'req': json.dumps(req)}, headers=H, timeout=30)
            if r.status_code == 429:
                raise RuntimeError('429 explore')
            w = [x for x in _j(r.text)['widgets'] if x['id'] == 'TIMESERIES'][0]
            r2 = s.get('https://trends.google.com/trends/api/widgetdata/multiline',
                       params={'hl': 'en-US', 'tz': 300, 'req': json.dumps(w['request']), 'token': w['token']},
                       headers=H, timeout=30)
            if r2.status_code != 200:
                raise RuntimeError(f'{r2.status_code} multiline')
            tl = _j(r2.text)['default']['timelineData']
            rows = []
            for p in tl:
                vals = []
                for fv in p['formattedValue']:
                    vals.append(0.5 if fv == '<1' else float(fv))
                rows.append([pd.Timestamp(int(p['time']), unit='s').date()] + vals)
            df = pd.DataFrame(rows, columns=['date'] + list(terms)).set_index('date')
            return df
        except Exception as e:
            print('retry', a, str(e)[:80], file=sys.stderr)
            time.sleep(60 * (a + 1))
            session = s = requests.Session()  # fresh cookies/connection after a block
    raise RuntimeError('failed ' + str(terms))


def related(term, timeframe='today 12-m', geo='US', cat=0, session=None):
    """Return dict with top/rising related queries for a single term."""
    s = session or requests.Session()
    req = {'comparisonItem': [{'keyword': term, 'geo': geo, 'time': timeframe}], 'category': cat, 'property': ''}
    r = s.get('https://trends.google.com/trends/api/explore',
              params={'hl': 'en-US', 'tz': 300, 'req': json.dumps(req)}, headers=H, timeout=30)
    out = {}
    for w in _j(r.text)['widgets']:
        if w['id'] in ('RELATED_QUERIES', 'RELATED_TOPICS'):
            r2 = s.get('https://trends.google.com/trends/api/widgetdata/relatedsearches',
                       params={'hl': 'en-US', 'tz': 300, 'req': json.dumps(w['request']), 'token': w['token']},
                       headers=H, timeout=30)
            d = _j(r2.text)['default']['rankedList']
            out[w['id']] = d
    return out


def run_batches(batches, timeframe, geo='US', cat=0, prefix='', pause=40):
    """batches: dict name -> list of terms. Saves each to raw/X09_gt_<prefix><name>.csv"""
    s = requests.Session()
    for name, terms in batches.items():
        out = os.path.join(RAW, f'X09_gt_{prefix}{name}.csv')
        if os.path.exists(out):
            print('skip', out); continue
        df = fetch(terms, timeframe, geo, cat, session=s)
        df.to_csv(out)
        print('saved', out, flush=True)
        time.sleep(pause)


if __name__ == '__main__':
    name, terms = sys.argv[1], sys.argv[2].split('|')
    tf = sys.argv[3] if len(sys.argv) > 3 else '2021-01-01 2026-10-06'
    geo = sys.argv[4] if len(sys.argv) > 4 else 'US'
    cat = int(sys.argv[5]) if len(sys.argv) > 5 else 0
    df = fetch(terms, tf, geo, cat)
    out = os.path.join(RAW, f'X09_gt_{name}.csv')
    df.to_csv(out)
    print(out)
    print(df.tail(24).to_string())
