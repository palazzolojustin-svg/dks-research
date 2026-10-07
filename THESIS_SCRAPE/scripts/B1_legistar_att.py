"""B1: list Legistar attachments (with retries) for given matter IDs; also print matter text (staff summary) if available.
Rerun: python B1_legistar_att.py <client> <matterId> [<matterId> ...]
"""
import sys, requests, time, re, html
c = sys.argv[1]
def get(u):
    for a in range(5):
        try:
            r = requests.get(u, timeout=60)
            if r.status_code == 200:
                return r.json()
        except Exception:
            pass
        time.sleep(4 * (a + 1))
    return None
for mid in sys.argv[2:]:
    print('##', mid)
    a = get(f"https://webapi.legistar.com/v1/{c}/matters/{mid}/attachments") or []
    for x in a:
        print('    att:', x.get('MatterAttachmentName'), '|', x.get('MatterAttachmentHyperlink'))
    vs = get(f"https://webapi.legistar.com/v1/{c}/matters/{mid}/versions") or []
    for v in vs[-1:]:
        t = get(f"https://webapi.legistar.com/v1/{c}/matters/{mid}/texts/{v['Key']}")
        if t:
            plain = t.get('MatterTextPlain') or re.sub('<[^>]+>', ' ', html.unescape(t.get('MatterTextRtf') or ''))
            print('    TEXT:', re.sub(r'\s+', ' ', plain)[:6000])
    time.sleep(1)
