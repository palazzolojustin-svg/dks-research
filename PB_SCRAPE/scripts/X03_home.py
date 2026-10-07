"""X03: owned-brand featuring on dicks.com / golfgalaxy.com homepages over time (Wayback).

For each month, takes up to N snapshots (HTTP 200, compressed length > 20KB, i.e. not a block page)
from raw/X03_cdx_home200.txt (or a CDX file you pass), fetches the raw HTML (id_ mode), and counts
distinct link destinations that are brand-specific: owned (DKS vertical brands) vs national brands.
Writes raw/X03_home_<site>.csv and raw/X03_home_<site>_owned_links.txt (owned link texts per snapshot).

Usage: python X03_home.py <cdx_file> <site_url> <tag> [per_month=2]
  python X03_home.py ..\raw\X03_cdx_home200.txt https://www.dickssportinggoods.com/ dsg 2
Rerun monthly: refresh the CDX file with X03_cdx.py first.
"""
import sys, os, re, csv, collections
from urllib.parse import urlparse
sys.path.insert(0, os.path.dirname(__file__))
from X03_fetch import fetch
from X03_anchors import anchors

OWN_HREF = re.compile(r"calia|vrst|maxfli|walter-hagen|alpine-design|/f/ethos|ethos-|fitness-gear|nishiki|top-flite|tommy-armour|/f/quest|quest-|"
                      r"dsg-(brand|clothing|shop|sporthood|team|apparel|men|women|kid|boy|girl|outerwear|fleece|jacket|legging|jogger|essential|collection|cold|sale|youth|golf)|/f/dsg$|dsg-brand", re.I)
OWN_TEXT = re.compile(r"\bCALIA\b|\bVRST\b|\bDSG\b|Maxfli|Walter Hagen|Alpine Design|\bETHOS\b|Fitness Gear|Nishiki|Top-?Flite|Tommy Armour|\bQuest\b", re.I)
NAT = re.compile(r"nike|jordan|adidas|under[- ]armour|hoka|on-cloud|shop-on\b|/f/on-|new[- ]balance|north[- ]face|columbia|yeti|stanley|carhartt|brooks|asics|puma|titleist|callaway|taylormade|"
                 r"\bugg\b|ugg-|birkenstock|vuori|lululemon|crocs|faherty|free[- ]people|fp[- ]movement|gymshark|new[- ]era|chubbies|marine[- ]layer|owala|brumate|hydrojug|joola|wilson|rawlings|easton|"
                 r"oakley|skechers|converse|\bvans\b|patagonia|salomon|saucony|mizuno|champion|starter|travismathew|peter[- ]millar|g/fore|\bping\b|cobra|bink|frost[- ]buddy|gatorade|burton|"
                 r"alo\b|beyond yoga|sweaty betty|rhone|mizuno|marucci|victus|bauer|ccm|the-north|kuhl|smartwool|cotopaxi|hydro[- ]flask|solo[- ]stove|traeger|blackstone|bowflex|nordictrack|peloton|hyperice|theragun|garmin", re.I)
SKIP = re.compile(r"protips|policy|help-desk|gift-cards|scorecard|stores|TrackOrder|OrderItemDisplay|facebook|twitter|instagram|youtube|pinterest|tiktok|sportsmatter|investors|jobs|myworkday|about-us|LogonForm|MyAccount", re.I)


def norm(h):
    p = urlparse(h)
    return (p.path or "/").rstrip("/").lower() + ("?" + p.query if p.query else "")


def analyse(html):
    an = anchors(html)
    dest = collections.OrderedDict()
    for h, tx, al, ar in an:
        if not h or h.startswith("#") or SKIP.search(h):
            continue
        k = norm(h)
        lab = " ".join(x for x in (tx, al, ar) if x)
        dest.setdefault(k, set()).add(lab)
    own, nat, gen = [], [], []
    for k, labs in dest.items():
        lab = " / ".join(sorted(l for l in labs if l))[:120]
        if OWN_HREF.search(k) or OWN_TEXT.search(lab):
            own.append((k, lab))
        elif NAT.search(k) or NAT.search(lab):
            nat.append((k, lab))
        else:
            gen.append((k, lab))
    return own, nat, gen


def main(cdxfile, site, tag, per_month=2):
    rows = [l.split() for l in open(cdxfile, encoding="utf-8-sig") if l.strip() and l[0].isdigit()]
    rows = [r for r in rows if r[2] == "200" and r[3].isdigit() and int(r[3]) > 20000]
    bym = collections.defaultdict(list)
    for r in rows:
        bym[r[0][:6]].append(r)
    out = []
    owned_log = open(os.path.join(os.path.dirname(__file__), "..", "raw", f"X03_home_{tag}_owned_links.txt"), "w", encoding="utf-8")
    for m in sorted(bym):
        caps = bym[m]
        # spread picks across the month
        idx = sorted(set([0, len(caps) // 2, len(caps) - 1]))[:per_month] if per_month > 1 else [0]
        for i in idx:
            ts = caps[i][0]
            html = fetch(ts, caps[i][1])
            if not html or len(html) < 20000:
                continue
            own, nat, gen = analyse(html)
            tot = len(own) + len(nat)
            out.append([m, ts, len(own), len(nat), len(gen), round(len(own) / tot, 3) if tot else ""])
            owned_log.write(f"== {ts} own={len(own)} nat={len(nat)} gen={len(gen)}\n")
            for k, lab in own:
                owned_log.write(f"   {k} | {lab}\n".encode("ascii", "replace").decode())
            print(m, ts, len(own), len(nat), len(gen), flush=True)
    owned_log.close()
    with open(os.path.join(os.path.dirname(__file__), "..", "raw", f"X03_home_{tag}.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["month", "timestamp", "owned_brand_links", "national_brand_links", "generic_links", "owned_share_of_brand_links"])
        w.writerows(out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]) if len(sys.argv) > 4 else 2)
