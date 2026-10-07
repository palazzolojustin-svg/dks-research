"""B3: robust Legistar Web API helper (retries/backoff; the API resets connections when hit fast).
Rerun examples:
  python B3_legistar.py att <client> <matterId> [...]          -> attachments + histories
  python B3_legistar.py search <client> <term>                   -> matters whose title contains term (newest first, top 200)
  python B3_legistar.py events <client> <from> <to> [kw]         -> events + agenda items (filtered by kw) + attachments
  python B3_legistar.py get <url> <outfile>                       -> download a file (pdf/docx) to outfile
"""
import sys, time, requests

S = requests.Session()
S.headers.update({"User-Agent": "Mozilla/5.0 (research; palazzolojustin@gmail.com)"})


def get(u, p=None, tries=6, as_json=True):
    for i in range(tries):
        try:
            r = S.get(u, params=p, timeout=60)
            if r.status_code == 200:
                return r.json() if as_json else r
            print("HTTP", r.status_code, u)
        except Exception as e:
            print("retry", i, type(e).__name__)
        time.sleep(3 + 4 * i)
    return [] if as_json else None


def main():
    mode = sys.argv[1]
    if mode == "att":
        c = sys.argv[2]
        for mid in sys.argv[3:]:
            print("=== matter", mid)
            m = get(f"https://webapi.legistar.com/v1/{c}/matters/{mid}")
            if isinstance(m, dict):
                print("TITLE", m.get("MatterFile"), (m.get("MatterIntroDate") or "")[:10], (m.get("MatterTitle") or "")[:300])
            for a in get(f"https://webapi.legistar.com/v1/{c}/matters/{mid}/attachments"):
                print("ATT", a.get("MatterAttachmentName"), "|", a.get("MatterAttachmentHyperlink"))
            for a in get(f"https://webapi.legistar.com/v1/{c}/matters/{mid}/histories"):
                print("HIST", (a.get("MatterHistoryActionDate") or "")[:10], a.get("MatterHistoryActionName"), a.get("MatterHistoryPassedFlagName"), a.get("MatterHistoryEventId"))
            time.sleep(2)
    elif mode == "search":
        c, term = sys.argv[2], sys.argv[3]
        js = get(f"https://webapi.legistar.com/v1/{c}/matters",
                 {"$filter": f"substringof('{term}',MatterTitle) or substringof('{term}',MatterName)", "$top": "200", "$orderby": "MatterIntroDate desc"})
        print(f"== {c} '{term}': {len(js)} hits")
        for m in js:
            print(m["MatterId"], m.get("MatterFile"), (m.get("MatterIntroDate") or "")[:10], (m.get("MatterTitle") or m.get("MatterName") or "")[:250].replace("\n", " "))
    elif mode == "events":
        c, d0, d1 = sys.argv[2:5]
        kw = (sys.argv[5] if len(sys.argv) > 5 else "").lower()
        B = f"https://webapi.legistar.com/v1/{c}"
        ev = get(B + "/events", {"$filter": f"EventDate ge datetime'{d0}' and EventDate le datetime'{d1}'"})
        for e in ev:
            print("EVENT", e["EventId"], e["EventDate"][:10], e["EventBodyName"], "| agenda:", e.get("EventAgendaFile"), "| minutes:", e.get("EventMinutesFile"), "| video:", e.get("EventVideoPath"))
            items = get(B + f"/events/{e['EventId']}/eventitems", {"AgendaNote": "1", "MinutesNote": "1", "Attachments": "1"})
            for it in items:
                t = (it.get("EventItemTitle") or "")
                if kw and kw not in t.lower():
                    continue
                print("  ITEM", it.get("EventItemMatterId"), t[:200].replace("\n", " "))
                for a in it.get("EventItemMatterAttachments") or []:
                    print("     ATT", a.get("MatterAttachmentName"), "|", a.get("MatterAttachmentHyperlink"))
            time.sleep(2)
    elif mode == "get":
        r = get(sys.argv[2], as_json=False)
        if r is not None:
            open(sys.argv[3], "wb").write(r.content)
            print("saved", sys.argv[3], len(r.content))


if __name__ == "__main__":
    main()
