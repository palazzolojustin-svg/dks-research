"""X14: list factory-list / report links on archived DKS ESG 'policies-and-reporting' page snapshots.
Rerun: python X14_esg_page_links.py [timestamp ...]"""
import requests, re, time, sys
TS = sys.argv[1:] or ['20250114110142', '20241007152526', '20240520004746', '20231205200915']
for ts in TS:
    r = None
    for i in range(4):
        try:
            r = requests.get(f'https://web.archive.org/web/{ts}id_/https://investors.dicks.com/esg/policies-and-reporting/default.aspx', timeout=120); break
        except Exception as e:
            time.sleep(25)
    if r is None:
        print(ts, 'failed'); continue
    print(ts, r.status_code, len(r.text))
    for m in sorted(set(re.findall(r'href="([^"]+)"', r.text))):
        if any(k in m.lower() for k in ['transpar', 'factory', 'playbook', 'purpose', '.xlsx', 'supplier', 'report']):
            print('   ', m)
