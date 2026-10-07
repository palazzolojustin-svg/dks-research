"""B3: pull Legistar matter body text (staff memo text stored in MatterText) for given matters.
Rerun: python B3_legistar_text.py <client> <matterId> [...]  -> prints and saves raw/B3_<client>_<id>_text.txt
"""
import sys, os, time, re
from B3_legistar import get
RAW = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "raw")
c = sys.argv[1]
for mid in sys.argv[2:]:
    vers = get(f"https://webapi.legistar.com/v1/{c}/matters/{mid}/versions")
    print("=== matter", mid, "versions", [v.get("Value") for v in vers] if isinstance(vers, list) else vers)
    out = []
    for v in (vers if isinstance(vers, list) else []):
        t = get(f"https://webapi.legistar.com/v1/{c}/matters/{mid}/texts/{v['Key']}")
        if isinstance(t, dict):
            plain = t.get("MatterTextPlain") or ""
            if not plain and t.get("MatterTextRtf"):
                plain = re.sub(r"\\[a-z]+-?\d* ?|[{}]", " ", t["MatterTextRtf"])
            out.append(f"--- version {v.get('Value')} ---\n{plain}")
        time.sleep(1.5)
    txt = "\n".join(out)
    open(os.path.join(RAW, f"B3_{c}_{mid}_text.txt"), "w", encoding="utf-8").write(txt)
    print(txt[:6000])
    time.sleep(2)
