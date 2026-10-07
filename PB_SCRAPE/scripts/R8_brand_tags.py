"""R8: brand tags in DKS-bound BOL descriptions, comparable samples:
 (A) the DMSC company page's own "recent shipments" list (most recent ~50 DKS BOLs, all suppliers) in the 2025-09-06 Wayback snapshot vs the
     2026-10-07 live page;  (B) the full 2026 BOL sample from supplier pages restricted to complete windows, by month (Jun-Sep 2026).
Tags reuse X04's regex set plus R8 additions. Input raw/X04_dks_bols_tagged.csv, raw/R8_bols_all.csv. Output raw/R8_brand_tags.csv
"""
import os, re
import pandas as pd
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "raw")
TAGS = {"DSG": r"\bdsg\b|dicks? logo|\bdcsg\b", "CALIA": r"calia|truelight|effortless", "VRST": r"\bvrst\b|limitless",
        "MAXFLI": r"maxfli|softfli|straightfli|strtfl|softfl", "TOP-FLITE": r"topfli|top fli|tfxl", "ETHOS": r"\bethos\b", "NISHIKI": r"nishiki",
        "QUEST": r"\bquest\b", "WALTER HAGEN(MGA/WGH code)": r"walter hagen|\bmga\b|\bwgh\b", "ALPINE DESIGN": r"alpine", "FITNESS GEAR": r"fitness gear",
        "DSG women/girls codes (DAW/DAG)": r"\bdaw\b|\bdag\b"}
NATL = r"kijaro|sole |treadmill|bowflex|schwinn|lifetime|intex|bestway|goleader|freestyle rocker|comfort pro|horizon treadmill|griddle"


def tags(s):
    return [k for k, p in TAGS.items() if re.search(p, str(s), re.I)]


x = pd.read_csv(os.path.join(RAW, "X04_dks_bols_tagged.csv"))
x["month"] = x.date.str[:7]
rows = []
for lab, g in x.groupby("sample"):
    n = len(g); r = {"sample": lab, "n_bols": n, "months": f"{g.month.min()}..{g.month.max()}"}
    anyown = g.description.apply(lambda s: len(tags(s)) > 0)
    r["any_owned_brand_tag_share"] = round(anyown.mean(), 3)
    r["national_brand_text_share"] = round(g.description.str.contains(NATL, case=False, regex=True).mean(), 3)
    for k in TAGS:
        r[k] = int(g.description.apply(lambda s: k in tags(s)).sum())
    rows.append(r)
o = pd.DataFrame(rows)
o.to_csv(os.path.join(RAW, "R8_brand_tags.csv"), index=False)
if __name__ == "__main__":
    pd.set_option("display.width", 250)
    print(o.T.to_string())
    print(x.groupby(["sample", "month"]).size().to_string())
