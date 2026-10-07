"""H03: list attachments + history for Legistar matters.
Rerun: python H03_legistar_att.py <client> <matterId> [matterId ...]
"""
import sys, requests, time
c = sys.argv[1]
for mid in sys.argv[2:]:
    print("=== matter", mid)
    for ep in ("attachments", "histories"):
        try:
            js = requests.get(f"https://webapi.legistar.com/v1/{c}/matters/{mid}/{ep}", timeout=60).json()
        except Exception as e:
            print(ep, "ERR", e); continue
        for a in js:
            if ep == "attachments":
                print("ATT", a.get("MatterAttachmentName"), "|", a.get("MatterAttachmentHyperlink"))
            else:
                print("HIST", (a.get("MatterHistoryActionDate") or "")[:10], a.get("MatterHistoryActionName"), a.get("MatterHistoryPassedFlagName"))
        time.sleep(1)
