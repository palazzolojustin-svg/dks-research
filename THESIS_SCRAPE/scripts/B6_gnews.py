"""B6: Google News RSS search (titles + source + date + link). Rerun: python B6_gnews.py "q1" "q2" ... -> appends raw/B6_gnews.csv
"""
import requests, re, sys, csv, time, html
H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/127.0'}
w = csv.writer(open(r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\B6_gnews.csv', 'a', newline='', encoding='utf-8'))
for q in sys.argv[1:]:
    u = 'https://news.google.com/rss/search?q=' + requests.utils.quote(q) + '&hl=en-US&gl=US&ceid=US:en'
    try:
        r = requests.get(u, headers=H, timeout=30)
    except Exception as e:
        print('ERR', q, str(e)[:80]); time.sleep(5); continue
    items = re.findall(r'<item>(.*?)</item>', r.text, re.S)
    print('==', q, r.status_code, len(items))
    for it in items[:30]:
        g = lambda tag: html.unescape((re.search(f'<{tag}[^>]*>(.*?)</{tag}>', it, re.S) or [None, ''])[1])
        t, d, l, s = g('title'), g('pubDate'), g('link'), g('source')
        w.writerow([q, d, t, s, l]); print('  ', d[5:16], '|', t[:150])
    time.sleep(3)
