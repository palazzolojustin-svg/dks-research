"""X14: download DKS vertical-brand factory disclosure lists (Human Rights Watch Transparency Pledge lists) and Purpose Playbooks
from the Wayback Machine (q4cdn returns 403 to scripts), then try live CDN for newer, guessed versions.
Rerun: python X14_fetch_factory_lists.py   -> files land in PB_SCRAPE/raw/X14_fl_*.{pdf,xlsx}
To find NEW versions: rerun X14_wayback_cdx.py "s27.q4cdn.com/812551136/files/*" and grep for "Transparency".
"""
import requests, os, time
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'raw')
FILES = {
 'X14_fl_2020-09.pdf': 'https://s27.q4cdn.com/812551136/files/doc_downloads/csr/Compliance_-_Transparency_Pledge_09302020.pdf',
 'X14_fl_2023-01.xlsx': 'https://s27.q4cdn.com/812551136/files/doc_downloads/2023/01/Test-Schedule-Report-for-Compliance-Transparency-Pledge-by-HKSystemSupport_2023-01-01_090000.xlsx',
 'X14_fl_2023-07.xlsx': 'https://s27.q4cdn.com/812551136/files/doc_downloads/2023/07/Test-Schedule-Report-for-Compliance-Transparency-Pledge-by-HKSystemSupport_2023-07-01_090000.xlsx',
 'X14_fl_2024-07.xlsx': 'https://s27.q4cdn.com/812551136/files/doc_downloads/2024/07/Test-Schedule-Report-for-Compliance-Transparency-Pledge-by-VerticalBrandsSupport_2024-07-01_090508.xlsx',
 'X14_pp_2019.pdf': 'https://s27.q4cdn.com/812551136/files/doc_downloads/2019PurposePlaybook.pdf',
 'X14_pp_2020.pdf': 'https://s27.q4cdn.com/812551136/files/doc_downloads/2020PurposePlaybook.pdf',
 'X14_pp_2021.pdf': 'https://s27.q4cdn.com/812551136/files/doc_downloads/2021/playbook/DSG_2021ESGReport_Final.pdf',
}
for fn, u in FILES.items():
    out = os.path.join(RAW, fn)
    if os.path.exists(out) and os.path.getsize(out) > 1000:
        print('have', fn); continue
    for attempt in range(3):
        try:
            r = requests.get('https://web.archive.org/web/2026id_/' + u, timeout=300)
            if r.status_code == 200 and len(r.content) > 1000:
                open(out, 'wb').write(r.content); print('ok', fn, len(r.content)); break
            print('status', r.status_code, fn)
        except Exception as e:
            print('err', fn, e)
        time.sleep(5)
