"""B6: date DKS's store scheduling tool (Kronos/JDA/Legion/...) from archived store-manager / ASM / operations job pages
(Wayback captures listed in raw/L3_cdx_jobs_v2.csv, 2019-2026). Fetches each capture (id_ raw mode) and greps tool names.
Rerun: python B6_wayback_tool_dating.py [max_per_year] -> raw/B6_wayback_tool_dating.csv
"""
import csv, re, requests, time, sys, collections
from bs4 import BeautifulSoup
RAW = r'C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw'
H = {'User-Agent': 'DKS research palazzolojustin@gmail.com'}
MAXY = int(sys.argv[1]) if len(sys.argv) > 1 else 40
TOOLS = re.compile(r'legion|kronos|\bUKG\b|reflexis|\bJDA\b|blue yonder|workforce management|workload planner|labor scheduling|scheduling (?:system|tool|software)|payroll budget|schedul\w+ tool|\bWFM\b', re.I)
rows = list(csv.DictReader(open(RAW + r'\L3_cdx_jobs_v2.csv', encoding='utf-8')))
sel = collections.defaultdict(list); seenurl = set()
for x in rows:
    y = x['timestamp'][:4]
    if x['statuscode'] != '200' or y < '2019': continue
    if not re.search(r'(?i)store-manager|assistant-store|operations-lead|operations-leader|asm|bench', x['original']): continue
    key = re.sub(r'\?.*', '', x['original'])
    if key in seenurl: continue
    seenurl.add(key); sel[y].append(x)
out = csv.writer(open(RAW + r'\B6_wayback_tool_dating.csv', 'w', newline='', encoding='utf-8'))
out.writerow(['timestamp', 'url', 'status', 'tools_found', 'context'])
for y in sorted(sel):
    lst = sel[y][:MAXY]; n = 0; hits = collections.Counter()
    for x in lst:
        u = f"https://web.archive.org/web/{x['timestamp']}id_/{x['original']}"
        try:
            r = requests.get(u, headers=H, timeout=60)
        except Exception as e:
            time.sleep(3); continue
        t = BeautifulSoup(r.text, 'html.parser').get_text(' ')
        t = re.sub(r'\s+', ' ', t)
        if 'store' not in t.lower(): continue
        n += 1
        found = sorted(set(m.group(0).lower() for m in TOOLS.finditer(t)))
        ctx = ''
        m = TOOLS.search(t)
        if m: ctx = t[max(0, m.start()-250):m.end()+250]
        for f in found: hits[f] += 1
        out.writerow([x['timestamp'], x['original'], r.status_code, ';'.join(found), ctx])
        time.sleep(0.8)
    print(y, 'pages parsed', n, dict(hits), flush=True)
