"""R9: table of usable (HTTP 200) Common Crawl captures by crawl, for dicks.com /f/ and /p/ (from X03's
CDX census in raw/X03_cc and X11's raw/X11_ccidx), golfgalaxy.com /f/, publiclands.com, calia.com, vrst.com
(from raw/R9/idx). Rerun: python R9_availability.py  → raw/R9_cc_availability.csv
"""
import collections, csv, glob, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from R9_cc_common import RAW, load_idx

CRAWL_MONTH = {  # approximate crawl months (CC announcements)
    "2022-05": "Jan-22", "2022-21": "May-22", "2022-27": "Jun-Jul-22", "2022-33": "Aug-22", "2022-40": "Sep-Oct-22",
    "2022-49": "Nov-Dec-22", "2023-06": "Jan-Feb-23", "2023-14": "Mar-Apr-23", "2023-23": "May-Jun-23",
    "2023-40": "Sep-Oct-23", "2023-50": "Nov-Dec-23", "2024-10": "Feb-Mar-24", "2024-18": "Apr-24",
    "2024-22": "May-24", "2024-26": "Jun-24", "2024-30": "Jul-24", "2024-33": "Aug-24", "2024-38": "Sep-24",
    "2024-42": "Oct-24", "2024-46": "Nov-24", "2024-51": "Dec-24", "2025-05": "Jan-25", "2025-08": "Feb-25",
    "2025-13": "Mar-25", "2025-18": "Apr-25", "2025-21": "May-25", "2025-26": "Jun-25", "2025-30": "Jul-25",
    "2025-33": "Aug-25", "2025-38": "Sep-25", "2025-43": "Oct-25", "2025-47": "Nov-25", "2025-51": "Dec-25",
    "2026-04": "Jan-26", "2026-08": "Feb-26", "2026-12": "Mar-26", "2026-17": "Apr-26", "2026-21": "May-26",
    "2026-25": "Jun-26", "2026-30": "Jul-26", "2026-34": "Aug-26", "2026-39": "Sep-26"}


def summ(rows, fpath_filter=None):
    st = collections.Counter(r.get("status") for r in rows if not fpath_filter or fpath_filter in r.get("url", ""))
    clean = sum(1 for r in rows if r.get("status") == "200" and "?" not in r.get("url", "")
                and (not fpath_filter or fpath_filter in r.get("url", "")))
    return len(rows), st.get("200", 0), st.get("403", 0), st.get("301", 0) + st.get("302", 0), clean


def main():
    out = collections.defaultdict(dict)
    for f in glob.glob(os.path.join(RAW, "X03_cc", "*_f.jsonl")):
        c = os.path.basename(f)[8:15]; out[c]["dks_f"] = summ(load_idx(f))
    for f in glob.glob(os.path.join(RAW, "X03_cc", "*_p.jsonl")):
        c = os.path.basename(f)[8:15]; out[c]["dks_p"] = summ(load_idx(f))
    for tag in ("gg_f", "pl_all", "calia_all", "vrst_all"):
        for f in glob.glob(os.path.join(RAW, "R9", "idx", f"CC-MAIN-*_{tag}.jsonl")):
            c = os.path.basename(f)[8:15]
            rows = load_idx(f)
            out[c][tag] = summ(rows, "/f/" if tag == "pl_all" else None)
    cols = ["dks_f", "dks_p", "gg_f", "pl_all", "calia_all", "vrst_all"]
    with open(os.path.join(RAW, "R9_cc_availability.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["crawl", "month"] + [f"{k}_{m}" for k in cols for m in ("n", "200", "403", "3xx", "clean200")])
        for c in sorted(out):
            w.writerow([c, CRAWL_MONTH.get(c, "")] + [x for k in cols for x in (out[c].get(k) or ("", "", "", "", ""))])
    for c in sorted(out):
        print(c, CRAWL_MONTH.get(c, ""), {k: out[c][k][4] for k in cols if k in out[c]},
              {k + "_403": out[c][k][2] for k in cols if k in out[c] and out[c][k][2]})


if __name__ == "__main__":
    main()
