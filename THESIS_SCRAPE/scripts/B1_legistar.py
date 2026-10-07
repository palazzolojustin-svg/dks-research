"""B1: Legistar Web API search of matter titles (and optionally list attachments).
Rerun: python B1_legistar.py <client> "<term1>|<term2>" [since=2024-01-01]   -> lists matches + attachment names/URLs
"""
import sys, requests, time
c = sys.argv[1]
terms = sys.argv[2].split('|')
since = sys.argv[3] if len(sys.argv) > 3 else '2024-01-01'
seen = set()
for t in terms:
    tt = t.replace("'", "''")
    params = {"$filter": f"(substringof('{tt}',MatterTitle) or substringof('{tt}',MatterName)) and MatterIntroDate ge datetime'{since}'", "$top": "100"}
    try:
        r = requests.get(f"https://webapi.legistar.com/v1/{c}/matters", params=params, timeout=60)
    except Exception as e:
        print('ERR', e); continue
    if r.status_code != 200:
        print(c, t, 'HTTP', r.status_code, r.text[:150]); continue
    for m in r.json():
        if m['MatterId'] in seen: continue
        seen.add(m['MatterId'])
        print(f"## {m['MatterId']} {m.get('MatterFile')} {(m.get('MatterIntroDate') or '')[:10]} | {(m.get('MatterTitle') or m.get('MatterName') or '')[:400]}")
        try:
            a = requests.get(f"https://webapi.legistar.com/v1/{c}/matters/{m['MatterId']}/attachments", timeout=60).json()
            for x in a:
                print('    att:', x.get('MatterAttachmentName'), '|', x.get('MatterAttachmentHyperlink'))
        except Exception as e:
            print('    att ERR', e)
        time.sleep(0.3)
