"""H03: search Legistar Web API matters for a term across city clients.
Rerun: python H03_legistar.py <term> <client1> [client2 ...]
Prints MatterId, file#, intro date, title. Then use matter attachments endpoint:
 https://webapi.legistar.com/v1/<client>/matters/<id>/attachments
"""
import sys, requests, json
term = sys.argv[1]
for c in sys.argv[2:]:
    u = f"https://webapi.legistar.com/v1/{c}/matters"
    params = {"$filter": f"substringof('{term}',MatterTitle) or substringof('{term}',MatterName)", "$top": "100"}
    try:
        r = requests.get(u, params=params, timeout=60)
        if r.status_code != 200:
            print(c, "HTTP", r.status_code, r.text[:200]); continue
        js = r.json()
        print(f"== {c}: {len(js)} hits")
        for m in js:
            print(m["MatterId"], m.get("MatterFile"), (m.get("MatterIntroDate") or "")[:10], (m.get("MatterTitle") or m.get("MatterName") or "")[:300].replace("\n", " "))
    except Exception as e:
        print(c, "ERR", e)
