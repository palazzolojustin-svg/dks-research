"""H03: list Legistar events in a date range and their agenda items' matter attachments containing a keyword.
Rerun: python H03_legistar_events.py <client> <from YYYY-MM-DD> <to YYYY-MM-DD> [keyword]
"""
import sys, requests, time
c, d0, d1 = sys.argv[1:4]; kw = (sys.argv[4] if len(sys.argv) > 4 else "").lower()
B = f"https://webapi.legistar.com/v1/{c}"


def get(u, p=None):
    for i in range(4):
        try:
            return requests.get(u, params=p, timeout=30).json()
        except Exception as e:
            time.sleep(4)
    return []


ev = get(B + "/events", {"$filter": f"EventDate ge datetime'{d0}' and EventDate le datetime'{d1}'"})
for e in ev:
    print("EVENT", e["EventId"], e["EventDate"][:10], e["EventBodyName"], "| agenda:", e.get("EventAgendaFile"), "| minutes:", e.get("EventMinutesFile"))
    items = get(B + f"/events/{e['EventId']}/eventitems", {"AgendaNote": "1", "MinutesNote": "1", "Attachments": "1"})
    for it in items:
        t = (it.get("EventItemTitle") or "")
        if kw and kw not in t.lower():
            continue
        print("  ITEM", it.get("EventItemMatterId"), t[:200].replace("\n", " "))
        for a in it.get("EventItemMatterAttachments") or []:
            print("     ATT", a.get("MatterAttachmentName"), "|", a.get("MatterAttachmentHyperlink"))
    time.sleep(1)
