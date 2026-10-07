"""P4: what 3Q26/4Q26/1Q27/2Q27 DICK'S ticket do history and 2-yr stacks imply, vs consensus comp?
Uses raw/P4_ticket_history.csv (reported quarters). Prints:
 (1) distribution of q/q changes in ticket growth (non-COVID), largest decelerations;
 (2) 2-yr-stack scenarios for ticket and transactions for 3Q26-2Q27;
 (3) implied comp vs Bloomberg consensus comp and $ variance (DKS segment rev base from P4_consensus_ticket_check).
Rerun: python P4_ticket_stack_scenarios.py -> raw/P4_ticket_stack_scenarios.csv
"""
import csv, os, statistics as st
RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw"
rows = [r for r in csv.DictReader(open(os.path.join(RAW, "P4_ticket_history.csv"))) if r["type"] == "reported"]
order = []
for fy in range(12, 27):
    for q in (1, 2, 3, 4):
        p = f"Q{q}FY{fy}"
        m = [r for r in rows if r["period"] == p]
        if m: order.append((p, float(m[0]["ticket_pct"]), float(m[0]["transactions_pct"])))
covid = {f"Q{q}FY{y}" for q in (1, 2, 3, 4) for y in (20, 21)} | {"Q1FY22"}
idx = {p: i for i, (p, _, _) in enumerate(order)}
ch = []
for i in range(1, len(order)):
    a, b = order[i - 1], order[i]
    if a[0] in covid or b[0] in covid: continue
    # only consecutive quarters (Q4 often missing in 10-Q series)
    pa, pb = a[0], b[0]
    qa, fa = int(pa[1]), int(pa[4:]); qb, fb = int(pb[1]), int(pb[4:])
    if not ((fb == fa and qb == qa + 1) or (fb == fa + 1 and qa == 4 and qb == 1)): continue
    ch.append((pb, round(b[1] - a[1], 1)))
d = [c for _, c in ch]
print("consecutive q/q ticket changes n=%d mean %.2f sd %.2f; <= -2.0pt: %s" % (len(d), st.mean(d), st.pstdev(d), [c for c in ch if c[1] <= -2.0]))
T = {p: (t, x) for p, t, x in order}
# 2-yr stacks: target quarter's ticket = stack - LY ticket
LY = {"3Q26": T["Q3FY25"], "4Q26": T["Q4FY25"], "1Q27": T["Q1FY26"], "2Q27": T["Q2FY26"]}
cons = {"3Q26": (1.69, 3334.4), "4Q26": (1.59, 4122.8), "1Q27": (2.41, 3501.7), "2Q27": (2.24, 4000.7)}
last_stack_t = T["Q2FY26"][0] + T["Q2FY25"][0]   # 3.6 + 4.1 = 7.7
last_stack_x = T["Q2FY26"][1] + T["Q2FY25"][1]   # 1.3 + 0.9 = 2.2
print("Q2FY26 2-yr stack ticket %.1f txn %.1f" % (last_stack_t, last_stack_x))
out = []
for name, dstack in [("stack_held", 0.0), ("stack_-1.5 (Q1->Q2 FY26 decel)", -1.5), ("stack_-3.0", -3.0)]:
    for qn, (lyt, lyx) in LY.items():
        t = last_stack_t + dstack - lyt
        x = last_stack_x - lyx
        comp = ((1 + t / 100) * (1 + x / 100) - 1) * 100
        c, rev = cons[qn]
        drev = rev / (1 + c / 100) * (comp - c) / 100
        out.append([name, qn, round(t, 2), round(x, 2), round(comp, 2), c, round(comp - c, 2), round(drev, 1)])
with open(os.path.join(RAW, "P4_ticket_stack_scenarios.csv"), "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["scenario", "qtr", "ticket", "txn_stack_held", "comp", "cons_comp", "comp_gap_pts", "d_DKS_rev_$M"]); w.writerows(out)
for o in out: print(o)
