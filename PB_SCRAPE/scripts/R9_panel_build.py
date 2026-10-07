"""R9: build a MATCHED-URL panel of dicks.com /f/ category pages captured by Common Crawl in each of
several seasonal windows, so owned-brand share can be compared on the SAME pages over time
(controls for CC's changing URL mix).

Rerun: python R9_panel_build.py
Windows (crawl preference order within each window = seasonal closeness to Aug-Sep):
  W23  = CC-MAIN-2023-40, 2023-50, 2024-10        (Sep-2023 .. Mar-2024)
  W25  = CC-MAIN-2025-38, 2025-33                 (Aug-Sep 2025)
  W26  = CC-MAIN-2026-39, 2026-34                 (Aug-Sep 2026)
  S23  = CC-MAIN-2023-23                          (May-Jun 2023)
  S26  = CC-MAIN-2026-25, 2026-21                 (May-Jun 2026)
Output: raw/R9/idx/panel_<name>_<crawl>.jsonl  (CDX records to fetch with R9_cc_extract.py, tag 'panel')
Index source: raw/X03_cc/<crawl>_f.jsonl (X03's full CDX census) – rerun X03_cc_census.py / R9_cc_index.py
for new crawls.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from R9_cc_common import load_idx, RAW

IDX = os.path.join(RAW, "X03_cc")
OUT = os.path.join(RAW, "R9", "idx")
os.makedirs(OUT, exist_ok=True)
PANELS = {"A": [["CC-MAIN-2023-40", "CC-MAIN-2023-50", "CC-MAIN-2024-10"], ["CC-MAIN-2025-38", "CC-MAIN-2025-33"],
                ["CC-MAIN-2026-39", "CC-MAIN-2026-34"]],
          "B": [["CC-MAIN-2023-23"], ["CC-MAIN-2026-25", "CC-MAIN-2026-21"]]}


SRC = {"A": os.path.join(IDX, "{c}_f.jsonl"), "B": os.path.join(IDX, "{c}_f.jsonl"),
       "G": os.path.join(RAW, "R9", "idx", "{c}_gg_f.jsonl")}  # G = golfgalaxy.com panel
PANELS["G"] = [["CC-MAIN-2023-40", "CC-MAIN-2023-50", "CC-MAIN-2024-10", "CC-MAIN-2023-23"],
               ["CC-MAIN-2025-38", "CC-MAIN-2025-33", "CC-MAIN-2025-43"],
               ["CC-MAIN-2026-39", "CC-MAIN-2026-34", "CC-MAIN-2026-30"]]


def recs(c, pat=os.path.join(IDX, "{c}_f.jsonl")):
    d = {}
    for r in load_idx(pat.format(c=c)):
        if r.get("status") == "200" and "?" not in r["url"]:
            d.setdefault(r["url"].lower().rstrip("/"), r)
    return d


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else "".join(PANELS)
    for name, wins in PANELS.items():
        if name not in only:
            continue
        cache = {}
        for w in wins:
            for c in w:
                cache.setdefault(c, recs(c, SRC[name]))
        sets = [set().union(*[cache[c].keys() for c in w]) for w in wins]
        common = set.intersection(*sets)
        print("panel", name, "urls", len(common))
        for w in wins:
            chosen = {}
            for u in common:
                for c in w:
                    if u in cache[c]:
                        chosen.setdefault(c, []).append(cache[c][u]); break
            for c, L in chosen.items():
                with open(os.path.join(OUT, f"panel_{name}_{c}.jsonl"), "w", encoding="utf-8") as f:
                    for r in L:
                        f.write(json.dumps(r) + "\n")
                print("  ", c, len(L))


if __name__ == "__main__":
    main()
