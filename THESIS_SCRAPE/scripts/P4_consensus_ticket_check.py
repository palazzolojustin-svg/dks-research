"""P4: internal-consistency test of Bloomberg consensus ticket/transaction rows vs consensus comp,
plus DKS ticket/transaction history (FY2012-Q2 FY26) and ticket scenarios -> comp/revenue/EPS variance.
Inputs are typed in from SOURCE/06_BLOOMBERG_FINANCIALS/DKS/DKS_Bloomberg-Financials_Quarterly_setA/setB.md and
_Annual_FY2022-FY2031E.md (pulled 2026-10-04) and 10-Q/10-K MD&A (raw/P4_edgar_ticket_sentences.csv).
Rerun: python P4_consensus_ticket_check.py  -> raw/P4_consensus_ticket_check.csv, raw/P4_ticket_scenarios.csv
"""
import csv, os
RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw"

# Bloomberg quarterly consensus (BBG label -> DKS fiscal qtr)
q = [  # (qtr, comp, ticket, txn, total_rev, FL_rev)
    ("3Q26E", 1.69, 1.25, 1.50, 5072.52, 1738.14),
    ("4Q26E", 1.59, 1.00, 1.57, 6262.29, 2139.45),
    ("1Q27E", 2.41, 1.00, 1.00, 5250.72, 1749.00),
    ("2Q27E", 2.24, 1.00, 1.00, 5726.00, 1725.35),
    ("3Q27E", 3.19, 1.00, 1.00, 5214.94, 1733.89),
    ("4Q27E", 3.23, 1.00, 1.00, 6452.44, 2174.61),
    ("1Q28E", 2.72, 1.00, 1.00, 5385.00, 1773.19),
    ("2Q28E", 2.72, 1.00, 1.00, 5899.00, 1749.74),
    ("3Q28E", 2.91, 1.00, 1.00, 5412.67, 1722.47),
    ("4Q28E", 2.76, 1.00, 1.00, 6654.50, 2214.16),
]
rows = []
for name, comp, t, x, rev, fl in q:
    implied = ((1 + t / 100) * (1 + x / 100) - 1) * 100
    gap = implied - comp
    tick_if_txn = ((1 + comp / 100) / (1 + x / 100) - 1) * 100  # ticket consistent with consensus comp if txn row is right
    rows.append([name, comp, t, x, round(implied, 2), round(gap, 2), round(tick_if_txn, 2), round(rev - fl, 1)])
with open(os.path.join(RAW, "P4_consensus_ticket_check.csv"), "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["qtr", "cons_comp", "cons_ticket_row", "cons_txn_row", "ticket_x_txn_implied_comp", "gap_vs_cons_comp_pts", "ticket_implied_by_cons_comp_if_txn_row_right", "DKS_seg_rev_implied_$M"])
    w.writerows(rows)
for r in rows: print(r)

# Annual check FY26E: actual Q1/Q2 + cons Q3/Q4 weighted by DKS segment revenue
qa = [(3377.4, 5.5, 0.5, 6.0), (3849.9, 3.6, 1.3, 4.9), (3334.4, 1.25, 1.50, 1.69), (4122.8, 1.00, 1.57, 1.59)]
W = sum(a[0] for a in qa)
print("FY26E weighted ticket %.2f txn %.2f comp %.2f  vs BBG annual ticket 2.76 txn 0.72 comp 3.37" % (
    sum(a[0] * a[1] for a in qa) / W, sum(a[0] * a[2] for a in qa) / W, sum(a[0] * a[3] for a in qa) / W))
qb = [(3501.7, 2.41), (4000.7, 2.24), (3481.1, 3.19), (4277.8, 3.23)]
print("FY27E weighted comp from qtrs %.2f vs BBG annual 2.60; annual ticket 1.00 x txn 1.00 = 2.01" % (sum(a * b for a, b in qb) / sum(a for a, _ in qb)))

# Scenario: 2H FY26 ticket vs consensus. Base = cons comp; alt = cons txn row held, ticket at X
H2 = {"3Q26E": (3334.4, 1.69, 1.50), "4Q26E": (4122.8, 1.59, 1.57)}
SH, TAX, FLOW = 89.09, 0.2746, 0.20
out = []
for tick in [1.0, 2.0, 2.6, 3.0, 3.6]:
    for txn_mode in ["cons_txn_row", "txn_0", "txn_-1"]:
        drev = 0
        for k, (rev, comp, txn) in H2.items():
            x = txn if txn_mode == "cons_txn_row" else (0.0 if txn_mode == "txn_0" else -1.0)
            newcomp = ((1 + tick / 100) * (1 + x / 100) - 1) * 100
            base = rev / (1 + comp / 100)  # approx comp base
            drev += base * (newcomp - comp) / 100
        eps = drev * FLOW * (1 - TAX) / SH
        out.append([tick, txn_mode, round(drev, 1), round(drev / 7457.2 * 1e4, 0), round(eps, 3)])
with open(os.path.join(RAW, "P4_ticket_scenarios.csv"), "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["2H_ticket_%", "txn_assumption", "d_rev_$M_vs_cons", "bps_of_2H_DKS_rev", "d_EPS_at_20pct_flow"]); w.writerows(out)
for r in out: print(r)
