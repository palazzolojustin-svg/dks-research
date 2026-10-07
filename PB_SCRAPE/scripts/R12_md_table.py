"""R12: render raw/R12_category_table.csv as a markdown table (owned/total = owned-brand X_BRAND facet count / all).
Columns: earliest of 22H1..23H2 (first available), 24A (Feb-May-24), 25B (Aug/Sep-25), 26A/25C (Nov-25..Jun-26),
26B (Jul-Sep-26), LIVE (07-Oct-26), deltas.
Rerun after R12_build_table.py:  python PB_SCRAPE\\scripts\\R12_md_table.py   (writes raw\\R12_category_table.md)
"""
import csv, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from R12_common import RAW
from R12_build_table import GROUP

rows = list(csv.DictReader(open(os.path.join(RAW, "R12_category_table.csv"), encoding="utf-8")))
MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


def cell(r, p):
    if not r.get(f"{p}_date"):
        return None
    return r[f"{p}_date"], int(r[f"{p}_owned"]), int(r[f"{p}_total"]), float(r[f"{p}_pct"])


def fmt(c):
    if not c:
        return "-"
    d = c[0]
    return f"{c[1]}/{c[2]} = {c[3]:.1f}% ({d[6:8]}-{MON[int(d[4:6]) - 1]}-{d[2:4]})"


out = ["| Group | Category (host) | Earliest 2022-23 | Feb-May 2024 | Aug/Sep-2025 | Nov-25 to Jun-26 | Jul-Sep-2026 (archive) | 07-Oct-2026 (live) | chg same-season y/y (pts) | chg Aug/Sep-25 to live (pts) |",
       "|---|---|---|---|---|---|---|---|---|---|"]
order = ["w_apparel", "m_apparel", "k_apparel", "golf_apparel", "golf_hard", "fitness", "outdoor", "team", "footwear"]
for r in sorted(rows, key=lambda r: (order.index(GROUP.get(r["slug"], "team")), r["slug"])):
    early = None
    for p in ("22H1", "22H2", "23H1", "23H2"):
        early = early or cell(r, p)
    a24, b25, b26, lv = cell(r, "24A"), cell(r, "25B"), cell(r, "26B"), cell(r, "LIVE")
    mid = cell(r, "26A") or cell(r, "25C")
    d1 = f"{b26[3] - b25[3]:+.1f}" if b25 and b26 else "-"
    d2 = f"{lv[3] - b25[3]:+.1f}" if b25 and lv else "-"
    out.append(f"| {GROUP.get(r['slug'], '')} | {r['slug']} ({r['host']}) | {fmt(early)} | {fmt(a24)} | {fmt(b25)} | "
               f"{fmt(mid)} | {fmt(b26)} | {fmt(lv)} | {d1} | {d2} |")
open(os.path.join(RAW, "R12_category_table.md"), "w", encoding="utf-8").write("\n".join(out) + "\n")
print("\n".join(out))
