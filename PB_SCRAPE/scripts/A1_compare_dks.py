"""A1 step 4: side-by-side fiscal-quarter series, Academy (ASO) vs DICK'S (R1), owned share of apparel reviews,
plus Nike share at each. Both retailers use a Feb-Jan fiscal year (Q1 Feb-Apr, Q2 May-Jul, Q3 Aug-Oct, Q4 Nov-Jan).
ASO variants: ALLX (ex-sampling), PURCH (post-purchase email+SMS; analogue of DKS PIE), EMAIL (email only; the one
program that runs unchanged 2023-2026). DKS = R1 PIE+ORG (raw/R1_chart_h2h_fq.csv).
Output: raw/A1_aso_vs_dks_fq.csv ; printed table.
RERUN: python A1_compare_dks.py  (after A1_analyze.py and R1_head2head.py)
"""
import csv, os, sys, collections
sys.path.insert(0, os.path.dirname(__file__))
from A1_bv_academy_common import RAW
from A1_analyze import load, BASKETS

def fq(y, m):
    if m == 1: return f"FY{(y - 1) % 100:02d}Q4"
    q = {2: 1, 3: 1, 4: 1, 5: 2, 6: 2, 7: 2, 8: 3, 9: 3, 10: 3, 11: 4, 12: 4}[m]
    return f"FY{y % 100:02d}Q{q}"


def main():
    rows = load()
    a = collections.defaultdict(lambda: [0, 0, 0])  # owned, nike, total
    for r in rows:
        for b, s in BASKETS.items():
            if r["basket"] in s:
                for v in ("ALLX", "PURCH", "EMAIL"):
                    if v in r["vars"]:
                        k = (b, fq(r["y"], r["m"]), v)
                        a[k][0] += r["owned"]; a[k][1] += r["brand"].lower() == "nike"; a[k][2] += 1
    d = {}
    for r in csv.DictReader(open(os.path.join(RAW, "R1_chart_h2h_fq.csv"), encoding="utf-8")):
        if r["brand"] in ("ALL OWNED", "Nike"):
            d[(r["basket"], r["fiscal_quarter"], r["brand"])] = (float(r["share_pie_plus_organic"]), int(r["total"]))
    out = []
    qs = sorted({k[1] for k in a if k[1] >= "FY23Q1"})
    for b in BASKETS:
        for q in qs:
            row = [b, q]
            for v in ("ALLX", "PURCH", "EMAIL"):
                o, n, t = a.get((b, q, v), [0, 0, 0])
                row += [round(o / t, 4) if t >= 30 else "", round(n / t, 4) if t >= 30 else "", t]
            do = d.get((b, q, "ALL OWNED")); dn = d.get((b, q, "Nike"))
            row += [round(do[0], 4) if do else "", round(dn[0], 4) if dn else "", do[1] if do else ""]
            out.append(row)
    hdr = ["basket", "fq", "aso_owned_allx", "aso_nike_allx", "aso_n_allx", "aso_owned_purch", "aso_nike_purch", "aso_n_purch",
           "aso_owned_email", "aso_nike_email", "aso_n_email", "dks_owned_pieorg", "dks_nike_pieorg", "dks_n"]
    with open(os.path.join(RAW, "A1_aso_vs_dks_fq.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(hdr); w.writerows(out)
    for r in out:
        print(*r, sep="\t")


if __name__ == "__main__":
    main()
