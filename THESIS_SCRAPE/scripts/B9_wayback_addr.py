"""B9: pull the street address of legacy DICK'S stores that a House of Sport replaced, from Wayback copies of the store-locator pages.
Rerun: python B9_wayback_addr.py  -> prints store, snapshot, address text; writes raw/B9_legacy_addr.txt
"""
import re
import requests

H = {"User-Agent": "IndependentResearch research-script contact@example.org"}
PAGES = {
    "Brandon #287": "fl/brandon/287",
    "Tampa #1130": "fl/tampa/1130",
    "Minnetonka #409": "mn/minnetonka/409",
    "Freehold #426": "nj/freehold/426",
    "Strongsville #193": "oh/strongsville/193",
    "Salem #1135": "nh/salem/1135",
}
out = []
for k, p in PAGES.items():
    try:
        cdx = requests.get("https://web.archive.org/cdx/search/cdx", params={"url": f"stores.dickssportinggoods.com/{p}/", "filter": "statuscode:200", "limit": "-2"}, headers=H, timeout=60).text.split("\n")
        ts = [l.split()[1] for l in cdx if l.strip()]
        if not ts:
            out.append(f"{k}: no snapshot")
            continue
        r = requests.get(f"https://web.archive.org/web/{ts[-1]}/http://stores.dickssportinggoods.com/{p}/", headers=H, timeout=90)
        t = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", r.text))
        m = re.search(r'"streetAddress"\s*:\s*"([^"]+)"', r.text)
        addr = m.group(1) if m else ""
        mall = re.findall(r"(?i)([A-Z][\w' ]{2,40}(?:Mall|Plaza|Center|Centre|Commons|Crossing|Town Center|Square|Village|Marketplace|Exchange))", t)[:4]
        out.append(f"{k} [{ts[-1]}]: street={addr} | names={mall}")
    except Exception as e:
        out.append(f"{k}: ERR {type(e).__name__}")
open(r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\B9_legacy_addr.txt", "w", encoding="utf-8").write("\n".join(out))
print("\n".join(out))
