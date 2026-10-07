"""H04: scan cached EDGAR docs (CMBS term sheets/prospectuses, REIT filings) for DICK'S / House of Sport
sales-table rows (anchor sales, sales PSF, occupancy cost) and lease terms.

Rerun: python H04_cmbs_sales.py [cache_dir]  -> prints matches; writes raw/H04_cmbs_dks_sales_snippets.txt
"""
import glob
import os
import re
import sys

CACHE = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\H04_edgar_cache"
OUT = r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw\H04_cmbs_dks_sales_snippets.txt"
rx = re.compile(r"(Dick'?’?s|DICK'?’?S)[^.]{0,40}(House of Sports?|Sporting Goods)", re.I)
num = re.compile(r"\$\s?\d[\d,\.]*|\d{1,3}\.\d%")
salesword = re.compile(r"sales|PSF|per square foot|occupancy cost|rent|percentage rent|kick|termination|co-tenancy|go dark|allowance|TI\b|tenant improvement", re.I)
seen = set()
with open(OUT, "w", encoding="utf-8") as out:
    for fp in sorted(glob.glob(os.path.join(CACHE, "*.txt"))):
        t = open(fp, encoding="utf-8").read()
        name = os.path.basename(fp)
        for m in rx.finditer(t):
            a, b = max(0, m.start() - 350), min(len(t), m.end() + 450)
            snip = t[a:b]
            if not (salesword.search(snip) and num.search(snip)):
                continue
            key = re.sub(r"\W", "", snip[300:600])[:120]
            if key in seen:
                continue
            seen.add(key)
            out.write(f"\n#### {name}\n{snip}\n")
print("done", len(seen))
