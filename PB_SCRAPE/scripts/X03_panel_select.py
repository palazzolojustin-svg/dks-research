"""X03: select panel slugs: (a) owned-brand pages, (b) generic category pages in categories where owned brands compete.
Usage: python X03_panel_select.py <pairs file> <out file>
"""
import sys, re
OWNED = re.compile(r"^f/(calia|vrst|dsg|maxfli|walter-hagen|alpine-design|ethos|fitness-gear|nishiki|quest|top-flite|tommy-armour)")
APP = re.compile(r"^f/(clearance-)?((womens|mens|boys|girls|kids|big-boy|big-girl|little-boys|little-girls|youth)-)?(big-and-tall-)?"
                 r"(athletic-|workout-|running-|training-|golf-|hiking-|cargo-)?(legging|jogger|shorts|hoodies|sweatshirts|jackets|fleece|shirts|tops|pants|sport-bras|sports-bras|socks|polos|skorts|swimsuits|compression)[a-z0-9\-]*$")
OTHER = re.compile(r"^f/(hats|mens-hats|boys-hats|girls-hats|womens-hats|hoodies-for-(women|men)|workout-pants-for-women|golf-[a-z\-]+|[a-z\-]*golf-(balls|bags|gloves|club-sets|clubs|apparel|shirts|pants|shorts|jackets)[a-z\-]*|"
                   r"[a-z0-9\-]*dumbbells|fitness-mats|gym-mats|yoga[a-z\-]*|[a-z\-]*tents|beach-chairs|camping-chairs|folding-portable-chairs|hiking-backpacks|backpacks-bags-sale|[a-z\-]*coolers|canopies[a-z\-]*|"
                   r"compression-apparel|matching-fleece-woven-sets|clearance-(mens|womens|apparel)|lightweight-layering-sale|fleece-clothing-under-60|hoodies-pants-sale|low-support-sports-bras|"
                   r"clothing-footwear-new-arrivals-sf|lady-hagen-shirts|kids-lightweight-layering-sale|long-sleeve-quarter-zip-tops-sale)$")
TEAM = re.compile(r"hockey|lacrosse|baseball|soccer|football|basketball|tennis|volleyball|wrestling|cheer|fishing|hunting|cycling|bike|ski|snow|winter|fan|team")
pairs = [l.strip() for l in open(sys.argv[1]) if l.strip()]
own = [s for s in pairs if OWNED.search(s)]
gen = [s for s in pairs if not OWNED.search(s) and (APP.search(s) or OTHER.search(s)) and not TEAM.search(s) and "x-brand" not in s and not re.search(r"-\d{5,}", s)]
print(len(own), len(gen))
print("\n".join(gen))
open(sys.argv[2], "w").write("\n".join(own + gen) + "\n")
