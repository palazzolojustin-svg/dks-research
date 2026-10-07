"""R5: classify owned-brand styles into sub-categories by name keywords and tabulate by season prefix.
Input : raw/R5_catalog_brands_<date>.csv (from R5_bv_catalog.py brands)
Output: raw/R5_owned_subcat_by_season.csv (brand_group, subcat, season, styles, skus)
        raw/R5_owned_footwear_styles.csv (curated footwear list)
Rerun : python R5_newcats.py [catalog csv]
"""
import re, sys, glob, os
import pandas as pd

RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\PB_SCRAPE\raw"
f = sys.argv[1] if len(sys.argv) > 1 else sorted(glob.glob(os.path.join(RAW, "R5_catalog_brands_*.csv")))[-1]
d = pd.read_csv(f, dtype=str)
d = d.drop_duplicates("product_id")
d["n_upc"] = d.n_upc.astype(int)
d["name"] = d.name.fillna("")
GROUP = {"Calia": "CALIA", "CALIA_by_Carrie_Underwood": "CALIA", "Walter_Hagen": "Walter Hagen", "Lady_Hagen": "Walter Hagen",
         "DICK_S_Sporting_Goods": "DSG", "Top_Flite": "Top Flite", "Tommy_Armour_Golf": "Tommy Armour",
         "Alpine_Design": "Alpine Design", "Fitness_Gear": "Fitness Gear", "Field___Stream": "Field & Stream"}
d["grp"] = d.brand_id.map(lambda b: GROUP.get(b, b))

FW = re.compile(r"\b(?:slides?|cleats?|shoes?|boots?|sandals?|sneakers?|flip[- ]?flops?|clogs?|slippers?|moccasins?|waders?)\b", re.I)
FW_X = re.compile(r"sock|bag|lace|insole|spray|deodor|cleaner|dryer|trainer|racer|single slide|dual slide|marker|kayak|anchor|"
                  r"tray|horn|cover|guard|tee\b|stake|boot ?cut|bands|skates?", re.I)
SUB = [  # order matters: first match wins
    ("footwear", None),
    ("golf", r"\bgolf\b|\bputters?\b|\bwedges?\b|\bdrivers?\b|\bhybrids?\b|\birons?\b|fairway|ball markers?|divot|golf tees?"),
    ("swim", r"swim|rash ?guard|board ?short|bikini|one[- ]piece|tankini|cover[- ]?up"),
    ("baseball/softball", r"t-?ball|tee ?ball|\bbats?\b|batting|glove|mitt|catcher|pitching|base set|\bbases\b"),
    ("denim", r"denim|jean"),
    ("dress", r"\bdress\b"),
    ("skirt/skort", r"skirt|skort"),
    ("outerwear", r"jacket|parka|puffer|\bvest\b|\bcoat\b|anorak|shell\b|insulated|rain"),
    ("fleece/hoodie", r"fleece|hood|sweatshirt|crew ?neck|pullover|quarter[- ]zip|1/4 zip|half[- ]zip|1/2 zip"),
    ("bra", r"\bbra\b|bralette"),
    ("legging/tight", r"legging|tights?\b|capri|bike short"),
    ("jogger/pant", r"jogger|\bpants?\b|chino|trouser|sweatpant"),
    ("short", r"\bshorts?\b"),
    ("polo/top/tee", r"polo|\btee\b|t-shirt|tank|top\b|shirt|long sleeve|henley|crop"),
    ("sleep/lounge", r"pajama|lounge|robe|sleep"),
    ("socks", r"\bsocks?\b"),
    ("hats/headwear", r"\bhat\b|\bcap\b|beanie|visor|headband|bucket"),
    ("bags", r"\bbag\b|backpack|duffle|tote|pack\b|sling|pouch"),
    ("baseball/softball", r"baseball|softball"),
    ("pickleball/tennis/racquet", r"pickleball|paddle|tennis|racquet"),
    ("soccer/football/basketball/lax/hockey/volley", r"soccer|football|basketball|lacrosse|hockey|volleyball|goal\b"),
    ("fitness equipment", r"dumbbell|kettlebell|bench|rack|plate|barbell|treadmill|bike trainer|rower|mat\b|band|weight|jump rope|foam roller|ab\b|bar\b"),
    ("bikes/scooters", r"\bbike\b|bicycle|scooter|helmet"),
    ("camping/outdoor", r"tent|sleeping|chair|cooler|canopy|hammock|lantern|stove|camp|table|grill|blanket|kayak|paddle board|fishing|rod|reel"),
    ("drinkware", r"bottle|tumbler|mug|jug|hydration"),
]
SUB_RE = [(n, re.compile(p, re.I) if p else None) for n, p in SUB]


def subcat(name):
    if FW.search(name) and not FW_X.search(name):
        return "footwear"
    for n, rx in SUB_RE[1:]:
        if rx.search(name):
            return n
    return "other"


def audience(name):
    n = name.lower()
    if re.search(r"toddler|kids'|kids |youth|boys'|girls'|boys |girls |little kids|big kids|infant|baby|preschool|grade school", n):
        return "kids"
    if re.search(r"women's|womens|ladies|lady", n):
        return "women"
    if re.search(r"men's|mens", n):
        return "men"
    return "unisex/na"


d["subcat"] = d.name.map(subcat)
d["aud"] = d.name.map(audience)
d["is_golf_apparel"] = d.name.str.contains(r"\bgolf\b", case=False) & ~d.grp.isin(["Maxfli", "Top Flite", "Tommy Armour"])
seasons = ["21", "22", "23", "24", "25", "26"]
x = d[d.pre.isin(seasons)]
out = x.groupby(["grp", "aud", "subcat", "pre"]).agg(styles=("product_id", "size"), skus=("n_upc", "sum")).reset_index()
out.to_csv(os.path.join(RAW, "R5_owned_subcat_by_season.csv"), index=False)
fw = d[d.subcat == "footwear"]
fw.to_csv(os.path.join(RAW, "R5_owned_footwear_styles.csv"), index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 500)
core = x[x.grp.isin(["DSG", "CALIA", "VRST", "Walter Hagen"])]
print("== styles by brand x subcat x season (core apparel brands) ==")
print(pd.crosstab([core.grp, core.subcat], core.pre).to_string())
print("== styles by brand x audience x season ==")
print(pd.crosstab([core.grp, core.aud], core.pre).to_string())
print("== golf-named apparel styles (non-golf-equipment brands) ==")
g = x[x.is_golf_apparel]
print(pd.crosstab(g.grp, g.pre).to_string())
print("== footwear styles / skus by brand x season ==")
fws = fw[fw.pre.isin([str(i) for i in range(15, 27)])]
print(pd.crosstab(fws.grp, fws.pre, margins=True).to_string())
print(fws.pivot_table(index="grp", columns="pre", values="n_upc", aggfunc="sum", margins=True).fillna(0).astype(int).to_string())
