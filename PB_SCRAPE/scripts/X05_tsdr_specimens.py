"""X05: For each DKS-owned trademark (from X05_uspto_dks_marks.json), pull the public TSDR document list and extract
specimen evidence from Applications / Statements of Use / responses: specimen description, specimen WEBPAGE URL
(usually a dicks.com or golfgalaxy.com product page = identifies brand + product), access date, first-use dates.

Rerun: python X05_uspto_tm_pull.py  then  python X05_tsdr_specimens.py [min_filed_year, default 2021]
Output: PB_SCRAPE/raw/X05_tsdr_specimens.csv
Method: public pages https://tsdr.uspto.gov/documentviewer?caseId=sn<serial> (embeds a DocsList JSON) and the
document web-content proxy https://tsdrsec.uspto.gov/ts/cd/tmcasedoc/downloadproxy?url=/api/casedoc/ts/cd/<sn>/<docId>/1/webcontent
No API key needed for these HTML views (the tsdrapi JSON API now needs a key).
"""
import csv, json, os, re, sys, time
import requests
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings('ignore')

H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128 Safari/537.36',
     'Referer': 'https://tsdr.uspto.gov/'}
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'raw')
WANT = ('Application', 'Statement of Use', 'Response to Office Action', 'Amendment to Allegation of Use',
        'Allegation of Use', 'Voluntary Amendment', 'Request for Extension of Time to File a Statement of Use')
MINY = sys.argv[1] if len(sys.argv) > 1 else '2021'


def dks(r):
    o = ' '.join(r['ownerName']).lower()
    return ('american sports licensing' in o or "dick's sporting" in o or 'golf galaxy, ' in o) and 'moosejaw' not in o


class _Resp:
    def __init__(self, content, ctype):
        self.content = content
        self.text = content.decode('utf-8', 'replace')
        self.headers = {'content-type': ctype}


def get(u):
    """Fetch with curl.exe (python-requests TLS handshakes were being reset in this environment)."""
    import subprocess
    for i in range(4):
        p = subprocess.run(['curl.exe', '-s', '-L', '--max-time', '60', '-A', H['User-Agent'], '-e', H['Referer'],
                            '-w', '\n__CT__%{content_type}', u], capture_output=True)
        if p.returncode == 0 and b'__CT__' in p.stdout:
            body, ct = p.stdout.rsplit(b'\n__CT__', 1)
            return _Resp(body, ct.decode())
        print('retry', i, u[-60:], p.returncode, flush=True)
        time.sleep(10 * (i + 1))
    raise RuntimeError('failed ' + u)


def docs_list(sn):
    t = get(f'https://tsdr.uspto.gov/documentviewer?caseId=sn{sn}').text
    m = re.search(r'var DocsList\s*=\s*(\{.*?\})\s*;?\s*</script>', t, re.S)
    return json.loads(m.group(1))['caseDocs'] if m else []


def doc_text(sn, docid):
    u = f'https://tsdrsec.uspto.gov/ts/cd/tmcasedoc/downloadproxy?url=/api/casedoc/ts/cd/{sn}/{docid}/1/webcontent'
    r = get(u)
    if 'html' not in r.headers.get('content-type', ''):
        return ''
    return BeautifulSoup(r.content, 'html.parser').get_text(' ', strip=True)


def grab(pat, t):
    return ' || '.join(dict.fromkeys(x.strip() for x in re.findall(pat, t)))


def main():
    R = [r for r in json.load(open(os.path.join(RAW, 'X05_uspto_dks_marks.json'), encoding='utf-8')) if dks(r)]
    R = [r for r in R if (r.get('filedDate') or '')[:4] >= MINY or (r.get('firstUseAnyDate') or '') >= '2024']
    only = os.environ.get('X05_SERIALS')  # optional comma list to restrict the run
    if only:
        R = [r for r in R if r['id'] in only.split(',')]
    outp = os.path.join(RAW, 'X05_tsdr_specimens.csv')
    done = set()
    if os.path.exists(outp):
        done = {row['serial'] for row in csv.DictReader(open(outp, encoding='utf-8'))}
    rows = []
    for r in sorted(R, key=lambda x: x['filedDate'], reverse=True):
        sn = r['id']
        if sn in done:
            continue
        try:
            docs = docs_list(sn)
        except Exception as e:
            print(sn, 'ERR', e); continue
        for d in docs:
            if not d['description'].startswith(WANT):
                continue
            try:
                t = doc_text(sn, d['docId'])
            except Exception as e:
                print(sn, 'doc ERR', d['docId'], e, flush=True)
                continue
            row = dict(serial=sn, wordmark=r['wordmark'], filed=r['filedDate'][:10], status=r['statusDescription'],
                       doc=d['description'], docDate=d['displayDate'],
                       specimen_desc=grab(r'SPECIMEN DESCRIPTION (.*?)(?: WEBPAGE URL| REQUEST| FEE| PAYMENT| SIGNATURE| SPECIMEN FILE|$)', t)[:400],
                       webpage_url=grab(r'WEBPAGE URL (\S+)', t)[:600],
                       webpage_access=grab(r'WEBPAGE DATE OF ACCESS (\S+)', t),
                       first_use=grab(r'FIRST USE ANYWHERE DATE (\S+)', t),
                       classes=' '.join(r['internationalClass']))
            rows.append(row)
            new = not os.path.exists(outp)
            with open(outp, 'a', newline='', encoding='utf-8') as f:
                w = csv.DictWriter(f, fieldnames=list(row.keys()))
                if new:
                    w.writeheader()
                w.writerow(row)
            print(sn, r['wordmark'], d['description'], row['webpage_url'][:120], row['specimen_desc'][:80], flush=True)
            time.sleep(2)
        time.sleep(2)
    print('rows', len(rows))


if __name__ == '__main__':
    main()

