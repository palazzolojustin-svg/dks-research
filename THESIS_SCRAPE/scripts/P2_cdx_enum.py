"""P2_cdx_enum.py: enumerate Wayback CDX captures (status 200, 2024-01-01 onward) of dickssportinggoods.com product pages (/p/<slug>) for a list of brand slug prefixes.
Rerun: python THESIS_SCRAPE\\scripts\\P2_cdx_enum.py  -> writes THESIS_SCRAPE\\raw\\P2_cdx_captures.csv (prefix,urlkey,timestamp,original,length)
Resumable: prefixes already present in the CSV are skipped.
"""
import requests, time, csv, os, sys
H = {'User-Agent': 'DKS price research (palazzolojustin@gmail.com)'}
CDX = 'http://web.archive.org/cdx/search/cdx'
OUT = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\P2_cdx_captures.csv'
PREFIXES = sys.argv[1:] or [
    'nike-mens-', 'nike-womens-', 'nike-kids-', 'nike-', 'jordan-', 'adidas-', 'hoka-', 'on-mens-', 'on-womens-', 'brooks-', 'new-balance-',
    'asics-', 'saucony-', 'under-armour-', 'the-north-face-', 'columbia-', 'patagonia-', 'yeti-', 'stanley-', 'hydro-flask-', 'owala-',
    'titleist-', 'callaway-', 'taylormade-', 'ping-', 'cobra-', 'rawlings-', 'easton-', 'wilson-', 'marucci-', 'victus-', 'louisville-slugger-',
    'bauer-', 'ccm-', 'garmin-', 'birkenstock-', 'crocs-', 'ugg-', 'lululemon-', 'vuori-', 'carhartt-', 'skechers-', 'converse-', 'vans-', 'puma-',
    'mizuno-', 'franklin-', 'selkirk-', 'joola-', 'spalding-', 'champion-', 'oakley-', 'costa-',
]
done = set()
if os.path.exists(OUT):
    with open(OUT, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            done.add(row['prefix'])
new = not os.path.exists(OUT)
f = open(OUT, 'a', newline='', encoding='utf-8')
w = csv.writer(f)
if new:
    w.writerow(['prefix', 'urlkey', 'timestamp', 'original', 'length'])
for pre in PREFIXES:
    if pre in done:
        continue
    params = {'url': 'dickssportinggoods.com/p/' + pre, 'matchType': 'prefix', 'output': 'json', 'fl': 'urlkey,timestamp,original,length',
              'filter': ['statuscode:200', 'mimetype:text/html'], 'from': '2024'}
    for attempt in range(5):
        try:
            r = requests.get(CDX, params=params, headers=H, timeout=600)
            if r.status_code == 200:
                rows = r.json()[1:] if r.text.strip() else []
                break
            print(pre, 'HTTP', r.status_code); time.sleep(30 * (attempt + 1))
        except Exception as e:
            print(pre, 'ERR', e); time.sleep(30 * (attempt + 1))
    else:
        print(pre, 'FAILED'); continue
    for x in rows:
        w.writerow([pre] + x)
    f.flush()
    print(pre, len(rows), flush=True)
    time.sleep(3)
f.close()
