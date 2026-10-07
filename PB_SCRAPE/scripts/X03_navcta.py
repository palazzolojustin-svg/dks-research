"""X03: extract the mega-menu "Featured" CTA links (linkTitle/link and flyout title/link) that dicks.com
embeds in every page's header JSON, for any cached Wayback snapshot (homepage or PLP).
These CTAs are merchandising's rotating promo slots (e.g. "Up to 60% Off DSG Clothing",
"CALIA: Designed to Move You"), so the owned-brand share of CTA slots is a marketing-priority series.

Usage: python X03_navcta.py <ts> <url>          -> prints CTAs, flags owned/national
Import: from X03_navcta import ctas, classify
"""
import sys, os, re
sys.path.insert(0, os.path.dirname(__file__))
from X03_fetch import fetch

OWN = re.compile(r"\bCALIA\b|\bVRST\b|\bDSG\b|Maxfli|Walter Hagen|Alpine Design|\bETHOS\b|Nishiki|Top[- ]?Flite|Tommy Armour|\bQuest\b|Only at DICK|only-at-dicks|onlyatdicks|"
                 r"calia|vrst|maxfli|walter-hagen|alpine-design|ethos-|/ethos|nishiki|top-flite|tommy-armour|X_BRAND%3AQuest|dsg-(?:brand|clothing|shop|team|apparel|kids|mens|womens|boys|girls|outerwear|fleece|sale|cold|essentials|collection|golf|youth|compression)", re.I)
NAT = re.compile(r"nike|jordan|adidas|under armour|under-armour|\bUA\b|hoka|on-cloud|shop-on\b|/f/on-|\bOn Running|new balance|new-balance|north face|north-face|columbia|yeti|stanley|carhartt|brooks|asics|puma|titleist|callaway|taylormade|"
                 r"\bugg\b|ugg-|birkenstock|vuori|crocs|faherty|free people|fp movement|gymshark|new era|chubbies|marine layer|owala|brumate|hydrojug|joola|wilson|rawlings|easton|oakley|skechers|converse|\bvans\b|patagonia|"
                 r"salomon|saucony|mizuno|champion|travismathew|peter millar|ping-golf|brand-shop/ping|\bPING\b|cobra|bowflex|nordictrack|peloton|garmin|solo stove|solo-stove|traeger|blackstone|coleman|\blifetime\b|spalding|bauer|marucci|victus|rhone|\balo\b|beyond yoga|sweaty betty|lululemon|hydro flask|smartwool|kuhl|primed|hey dude|skims|abercrombie|bogg|turtlebox|sole fitness|horizon", re.I)
DISC = re.compile(r"% off|\$\d+ off|\boff\b|sale|clearance|last[- ]chance|bogo|deal|buy \w+, get|save|under \$", re.I)

RX = re.compile(r'(?:"?linkTitle"?\s*:\s*"([^"]{1,140})"\s*,\s*"?link"?\s*:\s*"([^"]{0,300})")|(?:"?title"?\s*:\s*"([^"]{1,140})"\s*,\s*"?linkTitle"?\s*:\s*"[^"]*"\s*,\s*"?link"?\s*:\s*"([^"]{0,300})")|'
                r'(?:"?linkTitle"?\s*:\s*"[^"]*"\s*,\s*"?title"?\s*:\s*"([^"]{1,140})"\s*,\s*"?link"?\s*:\s*"([^"]{0,300})")')


def ctas(html):
    out = []
    seen = set()
    for m in RX.finditer(html):
        g = m.groups()
        title = g[0] or g[2] or g[4]
        link = g[1] if g[0] else (g[3] if g[2] else g[5])
        if title and (title, link) not in seen and not title.lower().startswith(("featured", "shop all", "explore now", "shop now")):
            seen.add((title, link))
            out.append((title, link or ""))
    return out


def classify(title, link):
    s = f"{title} {link}"
    if OWN.search(s):
        return "own"
    if NAT.search(s):
        return "nat"
    return "gen"


if __name__ == "__main__":
    t = fetch(sys.argv[1], sys.argv[2])
    for title, link in ctas(t):
        print(classify(title, link), "D" if DISC.search(title + " " + link) else "-", "|", title.encode("ascii", "replace").decode(), "|", link[:120])
