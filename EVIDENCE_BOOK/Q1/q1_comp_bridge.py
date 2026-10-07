"""EVIDENCE_BOOK Q1: definitive Q4 FY26 DICK'S-Business comp bridge (DKS long pitch).
Run:  python EVIDENCE_BOOK\\Q1\\q1_comp_bridge.py   (from C:\\Users\\palaz\\Downloads\\DKS_RESEARCH)
Writes EVIDENCE_BOOK\\Q1\\out\\*.csv and out\\tables.md (all tables used in EVIDENCE_BOOK\\Q1.md).

Inputs (all read-only; nothing under SOURCE / CORE_NOTES / WORKING_NOTES / THESIS_SCRAPE is modified):
- Comp history FY12-FY22: DKS 10-Q / 10-K MD&A and earnings 8-K EX-99.1 text pulled by THESIS_SCRAPE P4
  (THESIS_SCRAPE\\raw\\P4_edgar\\*.txt; sentences re-extracted by q1_extract_comps.py -> out\\edgar_comp_sentences.txt).
- Comp FY22Q3-FY26Q2: CORE_NOTES\\00_CORE_DIGEST.md s.2c/2d; C02_EARNINGS_CALLS_B.md l.24-41, 270.
- Ticket / transactions: THESIS_SCRAPE\\scripts\\P4_ticket_history.py table (re-keyed here; Q4 FY12-FY22 DERIVED).
- Consensus: SOURCE\\06_BLOOMBERG_FINANCIALS\\DKS\\DKS_Bloomberg-Financials_Quarterly_setA.md l.39-44, 119-123;
  setB l.39-44, 117-122 (printed 2026-10-04).
- Openings: THESIS_SCRAPE\\scripts\\B7_thesis1_model.py HIST/EVID schedule (10-Q counts + H02/H03/H05/H06/H07 dates),
  BBG store path (setA/setB l.76-78).
Everything labelled 'scenario' / 'engine' / 'implied' is INFERENCE.
"""
import csv, os, statistics as st

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUT, exist_ok=True)
MD = []                                                   # markdown tables collected for Q1.md
def md(title, header, rows, note=None):
    MD.append(f"\n### {title}\n")
    MD.append("| " + " | ".join(header) + " |")
    MD.append("|" + "---|" * len(header))
    for r in rows:
        MD.append("| " + " | ".join("" if v is None else (f"{v:.2f}" if isinstance(v, float) else str(v)) for v in r) + " |")
    if note:
        MD.append(f"\n{note}\n")
def wcsv(fn, header, rows):
    with open(os.path.join(OUT, fn), "w", newline="", encoding="utf-8") as f:
        c = csv.writer(f); c.writerow(header); c.writerows(rows)

TAX, SH = 0.2746, 89.09
EPS_PER_M = (1 - TAX) / SH                                # $/share per $1M pre-tax = 0.00814

# ------------------------------------------------------------------ 1. comp history
# comp: headline same-weeks basis (shifted/13-wk-comparable where the company gave it). src code:
#  R = reported quarter figure (10-Q/PR), S = reported shifted/calendar-adjusted, D = DERIVED from FY & 39-wk (INFERENCE),
#  C = corpus (digest / calls).  ticket/txn basis: FY12-FY16 'at Dick's Sporting Goods stores' (ex eCom & GG);
#  FY17-FY22 consolidated; FY23+ DICK'S Business. Q4 ticket/txn FY12-FY22 DERIVED (P4, (FY-0.68*39wk)/0.32).
H = [
 # q,       comp, src, alt(unshifted/orig), ticket, txn, tt_src
 ("FY12Q1", 8.4, "R", None, 4.0, 3.3, "R"), ("FY12Q2", 3.8, "R", None, 4.0, -1.1, "R"), ("FY12Q3", 5.1, "R", None, 2.9, 1.0, "R"),
 ("FY12Q4", 1.5, "D", None, 2.7, -4.7, "D"),
 ("FY13Q1", -3.8, "S", -1.7, 2.0, -5.2, "R"), ("FY13Q2", -0.4, "S", 1.2, 2.0, -1.9, "R"), ("FY13Q3", 3.3, "S", 0.3, 1.5, 1.9, "S"),
 ("FY13Q4", 7.3, "S", 5.9, 1.8, 5.2, "D"),
 ("FY14Q1", 1.5, "R", None, 2.5, -0.2, "R"), ("FY14Q2", 3.2, "R", None, 1.8, 2.3, "R"), ("FY14Q3", 1.1, "R", None, 2.7, -1.0, "R"),
 ("FY14Q4", 3.4, "R", None, 0.8, 2.9, "D"),
 ("FY15Q1", 1.0, "R", None, 1.0, 0.8, "R"), ("FY15Q2", 1.2, "R", None, 2.5, -1.0, "R"), ("FY15Q3", 0.4, "R", None, 1.2, -0.5, "R"),
 ("FY15Q4", -2.5, "R", None, 0.7, -3.1, "D"),
 ("FY16Q1", 0.5, "R", None, 1.0, -0.5, "R"), ("FY16Q2", 2.8, "R", None, 1.3, 1.7, "R"), ("FY16Q3", 5.2, "R", None, 1.3, 4.2, "R"),
 ("FY16Q4", 5.0, "R", None, 2.5, 2.7, "D"),
 ("FY17Q1", 2.4, "R", None, 1.6, 0.8, "R"), ("FY17Q2", 0.1, "R", None, 2.1, -2.0, "R"), ("FY17Q3", -0.9, "R", None, 0.0, -0.9, "R"),
 ("FY17Q4", -2.0, "R", None, -1.9, -0.1, "D"),
 ("FY18Q1", -2.5, "S", -0.9, 1.2, -3.7, "R"), ("FY18Q2", -4.0, "S", -1.9, 0.7, -4.7, "R"), ("FY18Q3", -3.9, "S", -6.1, 1.6, -5.5, "R"),
 ("FY18Q4", -2.2, "S", -3.7, 1.4, -3.7, "D"),
 ("FY19Q1", 0.0, "R", None, 1.0, -1.0, "R"), ("FY19Q2", 3.2, "R", None, 2.1, 1.1, "R"), ("FY19Q3", 6.0, "R", None, 2.7, 3.3, "R"),
 ("FY19Q4", 5.3, "R", None, 2.2, 2.8, "D"),
 ("FY20Q1", -29.5, "R", None, 9.2, -38.7, "R"), ("FY20Q2", 20.7, "R", None, 17.9, 2.8, "R"), ("FY20Q3", 23.2, "R", None, 19.6, 3.6, "R"),
 ("FY20Q4", 18.6, "D", None, None, None, "-"),
 ("FY21Q1", 115.0, "R", None, 25.0, 90.0, "R"), ("FY21Q2", 19.2, "R", None, 7.1, 12.1, "R"), ("FY21Q3", 12.2, "R", None, 3.7, 8.5, "R"),
 ("FY21Q4", 5.0, "D", None, None, None, "-"),
 ("FY22Q1", -8.4, "C", None, -2.0, -6.4, "R"), ("FY22Q2", -5.4, "C", None, 3.3, -8.4, "R"), ("FY22Q3", 6.5, "C", None, 2.8, 3.7, "R"),
 ("FY22Q4", 5.3, "C", None, -1.7, 5.7, "D"),
 ("FY23Q1", 3.4, "C", None, 0.7, 2.7, "C"), ("FY23Q2", 1.8, "C", None, -1.0, 2.8, "C"), ("FY23Q3", 1.7, "C", None, 0.6, 1.1, "C"),
 ("FY23Q4", 2.8, "C", None, 2.8, 0.0, "C"),
 ("FY24Q1", 5.3, "C", None, 2.6, 2.7, "C"), ("FY24Q2", 4.5, "C", None, 3.5, 1.0, "C"), ("FY24Q3", 4.3, "C", 4.2, 4.8, -0.6, "C"),
 ("FY24Q4", 6.6, "C", 6.4, 4.4, 2.0, "C"),
 ("FY25Q1", 4.5, "C", None, 3.7, 0.8, "C"), ("FY25Q2", 5.0, "C", None, 4.1, 0.9, "C"), ("FY25Q3", 5.7, "C", None, 4.4, 1.3, "C"),
 ("FY25Q4", 3.1, "C", None, 4.4, -1.3, "C"),
 ("FY26Q1", 6.0, "C", None, 5.5, 0.5, "C"), ("FY26Q2", 4.9, "C", None, 3.6, 1.3, "C"),
]
CONS = {"FY26Q3": 1.69, "FY26Q4": 1.59, "FY27Q1": 2.41, "FY27Q2": 2.24}          # BBG setA l.41
BBG_STACK = {"FY25Q1": 10.04, "FY25Q2": 9.73, "FY25Q3": 10.14, "FY25Q4": 9.70, "FY26Q1": 10.77, "FY26Q2": 10.15,
             "FY26Q3": 7.48, "FY26Q4": 4.74, "FY27Q1": 8.56, "FY27Q2": 7.25}       # BBG setA l.42 / setB l.42
COVID_Q = {f"FY{y}Q{q}" for y in (20, 21) for q in (1, 2, 3, 4)}
comp = {q: c for q, c, *_ in H}
tick = {q: t for q, c, s, a, t, x, ts in H}
txn = {q: x for q, c, s, a, t, x, ts in H}
tsrc = {q: ts for q, c, s, a, t, x, ts in H}
csrc = {q: s for q, c, s, a, t, x, ts in H}
QS = [h[0] for h in H]
def prev(q, k=4):
    fy, qq = int(q[2:4]), int(q[5]); i = (fy * 4 + qq - 1) - k
    return f"FY{i // 4:02d}Q{i % 4 + 1}"
def stk(q, n, series):
    vals = [series.get(prev(q, 4 * j)) for j in range(n)]
    return None if any(v is None for v in vals) else round(sum(vals), 2)
def covid_in(q, n):
    return any(prev(q, 4 * j) in COVID_Q for j in range(n))

rows = []
for q, c, s, a, t, x, ts in H:
    s2, s3 = stk(q, 2, comp), stk(q, 3, comp)
    chk = None if t is None else round(((1 + t / 100) * (1 + x / 100) - 1) * 100 - c, 1)
    rows.append([q, "Q4" if q.endswith("Q4") else "", c, s, a, t, x, ts, chk, s2, s3, stk(q, 2, tick), stk(q, 2, txn),
                 "COVID" if q in COVID_Q else ("stack incl COVID" if covid_in(q, 3) else "")])
HDR = ["quarter", "Q4", "comp_%", "comp_src", "alt_comp(unshifted/orig)", "ticket_%", "txn_%", "tt_src",
       "ticket*txn_minus_comp_pt", "2yr_stack", "3yr_stack", "ticket_2yr", "txn_2yr", "covid_flag"]
wcsv("q1_history.csv", HDR, rows)
md("T1. DICK'S comp, ticket, transactions and stacks, FY12-Q2 FY26 (additive stacks; Q4 rows in bold in Q1.md)",
   ["Qtr", "Q4", "Comp", "src", "alt", "Ticket", "Txn", "tt src", "2-yr", "3-yr", "Tkt 2-yr", "Txn 2-yr", "flag"],
   [[r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[9], r[10], r[11], r[12], r[13]] for r in rows],
   "src: R reported quarter; S reported shifted/calendar-adjusted (company's 'best view'); D derived from FY and 39-wk (INFERENCE, +-1pt); "
   "C corpus (digest s.2c-2d, calls). Ticket/txn FY12-16 = DSG stores ex-eCom (so ticket x txn != headline comp); FY17-22 consolidated; FY23+ DICK'S Business. "
   "Q4FY24 6.6 / Q3FY24 4.3 = restated figures management uses in its own stacks (orig 6.4 / 4.2).")

# ------------------------------------------------------------------ 2. consensus-implied stacks + ranking
cons_rows = []
for q, c in CONS.items():
    s2 = round(c + comp[prev(q)], 2); s3 = round(s2 + comp[prev(q, 8)], 2)
    geo = round(((1 + c / 100) * (1 + comp[prev(q)] / 100) - 1) * 100, 2)
    cons_rows.append([q, c, comp[prev(q)], comp[prev(q, 8)], s2, geo, BBG_STACK[q], s3])
wcsv("q1_consensus_stacks.csv", ["quarter", "cons_comp", "LY", "2Y_ago", "2yr_additive", "2yr_geometric", "BBG_2yr_row", "3yr_additive"], cons_rows)

def hist_vals(n, only_q4=False, ex_covid=True, start=None):
    out = []
    for q in QS:
        v = stk(q, n, comp)
        if v is None or (ex_covid and covid_in(q, n)) or (only_q4 and not q.endswith("Q4")):
            continue
        if start and int(q[2:4]) < start:
            continue
        out.append((q, v))
    return out
def pct_rank(x, vals):                       # % of history strictly below x (+ half ties)
    below = sum(v < x for v in vals); eq = sum(v == x for v in vals)
    return round(100 * (below + 0.5 * eq) / len(vals), 1)
rank_rows = []
for q, c, ly, y2, s2, geo, bbg, s3 in cons_rows:
    for label, n, x in (("2-yr", 2, s2), ("3-yr", 3, s3)):
        for uni, kw in (("all ex-COVID FY13-FY26Q2", {}), ("Q4s only ex-COVID", {"only_q4": True}),
                        ("post-COVID FY23-FY26Q2", {"start": 23}), ("pre-COVID FY13-FY19", {"start": 12})):
            hv = hist_vals(n, **kw)
            if uni.startswith("pre"):
                hv = [(qq, v) for qq, v in hv if int(qq[2:4]) <= 19]
            vals = [v for _, v in hv]
            if not vals:
                continue
            rank_rows.append([q, label, x, uni, len(vals), pct_rank(x, vals), round(min(vals), 2), round(st.median(vals), 2),
                              round(max(vals), 2), sum(v <= x for v in vals)])
wcsv("q1_stack_rank.csv", ["quarter", "stack", "cons_value", "universe", "n", "percentile", "min", "median", "max", "n_at_or_below"], rank_rows)
md("T2. Consensus-implied stacks (BBG comp row; additive = management convention; BBG's own row is geometric)",
   ["Qtr", "Cons comp", "LY", "2 yrs ago", "2-yr add.", "2-yr geo.", "BBG row", "3-yr add."], cons_rows)
md("T3. Where the consensus stacks rank vs history (percentile = share of history below it)",
   ["Qtr", "Stack", "Cons", "Universe", "n", "Pctile", "Min", "Median", "Max", "# hist <= cons"],
   [r for r in rank_rows if r[0] in ("FY26Q3", "FY26Q4")])
q4_hist = [(q, stk(q, 2, comp), stk(q, 3, comp)) for q in QS if q.endswith("Q4") and stk(q, 2, comp) is not None]
md("T3b. Every Q4 2-yr / 3-yr stack on record", ["Q4", "2-yr", "3-yr", "COVID in stack"],
   [[q, a, b, "yes" if covid_in(q, 3) else ""] for q, a, b in q4_hist] + [["FY26Q4E (cons)", cons_rows[1][4], cons_rows[1][7], ""]])

# q/q change in the 2-yr stack: how often has it fallen as much as consensus has it fall Q3->Q4 (and Q2->Q4)?
s2s = [(q, stk(q, 2, comp)) for q in QS if stk(q, 2, comp) is not None and not covid_in(q, 2)]
d1 = []
for (qa, a), (qb, b) in zip(s2s, s2s[1:]):
    if prev(qb, 1) == qa:
        d1.append((qb, round(b - a, 2)))
cons_d_q3q4 = round(cons_rows[1][4] - cons_rows[0][4], 2)
cons_d_q2q4 = round(cons_rows[1][4] - stk("FY26Q2", 2, comp), 2)
n_d1 = sum(v <= cons_d_q3q4 for _, v in d1)

# ------------------------------------------------------------------ 3. ticket grid + deceleration base rates
tr4_txn = round(st.mean([txn[q] for q in ("FY25Q3", "FY25Q4", "FY26Q1", "FY26Q2")]), 2)
tr8_txn = round(st.mean([txn[q] for q in ("FY24Q3", "FY24Q4", "FY25Q1", "FY25Q2", "FY25Q3", "FY25Q4", "FY26Q1", "FY26Q2")]), 2)
tr4_tkt = round(st.mean([tick[q] for q in ("FY25Q3", "FY25Q4", "FY26Q1", "FY26Q2")]), 2)
TXN_SCN = [("-1.3 (Q4FY25 actual)", -1.3), ("-0.5", -0.5), ("0.0", 0.0), (f"{tr4_txn} (trailing-4Q avg)", tr4_txn),
           ("+1.3 (Q2FY26 actual)", 1.3)]
def need_ticket(c, x):
    return round(((1 + c / 100) / (1 + x / 100) - 1) * 100, 2)
# historical ticket changes, ex-COVID, consecutive quarters only (pairs that touch FY20/FY21 excluded)
tq = [q for q in QS if tick[q] is not None]
d_q, d_2q, d_yy = [], [], []
for q in tq:
    p1, p2, p4 = prev(q, 1), prev(q, 2), prev(q, 4)
    bad = lambda *qq: any(z in COVID_Q or tick.get(z) is None for z in qq)
    if p1 in tick and not bad(q, p1):
        d_q.append((q, round(tick[q] - tick[p1], 2), tsrc[q] == "D" or tsrc[p1] == "D"))
    if p2 in tick and not bad(q, p1, p2):
        d_2q.append((q, round(tick[q] - tick[p2], 2), tsrc[q] == "D" or tsrc[p2] == "D"))
    if p4 in tick and not bad(q, p4):
        d_yy.append((q, round(tick[q] - tick[p4], 2), tsrc[q] == "D" or tsrc[p4] == "D"))
def cnt(lst, thr, reported_only=False):
    l = [v for q, v, d in lst if not (reported_only and d)]
    return sum(v <= thr for v in l), len(l)
grid = []
for qn, c, ref1, ref2, ref_ly in (("FY26Q3", 1.69, "FY26Q2", "FY26Q1", "FY25Q3"), ("FY26Q4", 1.59, "FY26Q3", "FY26Q2", "FY25Q4")):
    txn2 = round(st.mean([stk(z, 2, txn) for z in ("FY25Q3", "FY25Q4", "FY26Q1", "FY26Q2")]), 3)
    for lab, x in TXN_SCN + [(f"{round(txn2 - txn[ref_ly], 2)} (txn 2-yr held at trailing-4Q avg {txn2})", round(txn2 - txn[ref_ly], 2))]:
        t = need_ticket(c, x)
        if qn == "FY26Q3":
            dq = round(t - tick[ref1], 2); d2 = round(t - tick[ref2], 2)
        else:  # Q4: 1-quarter step vs the Q3 ticket implied at the SAME txn assumption; 2-quarter step vs Q2FY26 actual
            dq = None; d2 = round(t - tick["FY26Q2"], 2)
        dyy = round(t - tick[ref_ly], 2)
        n2, N2 = cnt(d_2q, d2); ny, Ny = cnt(d_yy, dyy); n2r, N2r = cnt(d_2q, d2, True)
        if dq is None:
            q1txt = "n/a (decel sits in Q3)"
        else:
            n1, N1 = cnt(d_q, dq); n1r, N1r = cnt(d_q, dq, True); q1txt = f"{n1}/{N1} ({n1r}/{N1r} rep.)"
        grid.append([qn, c, lab, t, round(t + tick[ref_ly], 2), dq, q1txt, d2, f"{n2}/{N2} ({n2r}/{N2r} rep.)",
                     dyy, f"{ny}/{Ny}"])
GH = ["quarter", "cons_comp", "txn_assumption", "ticket_needed", "ticket_2yr_stack", "chg_vs_prior_qtr_pt", "hist_qtrs_with_drop>=this (all/reported-only)",
      "chg_over_2_qtrs_pt", "hist_2q_drops>=this", "chg_vs_same_qtr_LY", "hist_yy_drops>=this"]
wcsv("q1_ticket_grid.csv", GH, grid)
md("T4. Ticket needed to hit consensus comp, by transaction assumption (ticket = (1+comp)/(1+txn)-1)",
   ["Qtr", "Cons", "Txn", "Ticket needed", "Tkt 2-yr", "chg q/q", "# hist q/q drops >= (all / reported-only)", "chg 2 qtrs", "# hist 2q drops >=",
    "chg vs LY qtr", "# hist y/y drops >="], grid,
   f"Q4 q/q left blank: if Q3 lands on consensus, Q4 needs ~no further ticket change at the same txn; the deceleration is concentrated in Q3. 'chg 2 qtrs' is vs Q2FY26 actual ticket 3.6%. "
   f"History = consecutive ex-COVID quarter pairs FY12-Q2FY26 (n q/q={len(d_q)}, 2q={len(d_2q)}, y/y={len(d_yy)}); 'reported-only' drops pairs that use a derived Q4. "
   f"Trailing-4Q txn avg {tr4_txn}%; trailing-8Q {tr8_txn}%; trailing-4Q ticket avg {tr4_tkt}%.")
big = sorted(d_q, key=lambda z: z[1])[:6]; big2 = sorted(d_2q, key=lambda z: z[1])[:6]; bigy = sorted(d_yy, key=lambda z: z[1])[:6]
md("T5. Largest ex-COVID ticket decelerations on record", ["Rank", "1-qtr (qtr, pt)", "2-qtr (qtr, pt)", "vs same qtr LY (qtr, pt)"],
   [[i + 1, f"{big[i][0]} {big[i][1]:+.1f}{' (D)' if big[i][2] else ''}", f"{big2[i][0]} {big2[i][1]:+.1f}{' (D)' if big2[i][2] else ''}",
     f"{bigy[i][0]} {bigy[i][1]:+.1f}{' (D)' if bigy[i][2] else ''}"] for i in range(6)],
   "(D) = involves a derived Q4 ticket. Q1FY26->Q2FY26 = -1.9pt (5.5 -> 3.6) is the latest print.")
wcsv("q1_ticket_changes.csv", ["quarter", "type", "chg_pt", "uses_derived_q4"],
     [[q, "q/q", v, d] for q, v, d in d_q] + [[q, "2q", v, d] for q, v, d in d_2q] + [[q, "y/y", v, d] for q, v, d in d_yy])

# ------------------------------------------------------------------ 4. HoS / FH format lift (monthly cohort engine)
FYS = ["FY23", "FY24", "FY25", "FY26", "FY27"]
MN = ["Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan"]
QL = [f"{fy}Q{q}" for fy in FYS for q in (1, 2, 3, 4)]
NM = len(QL) * 3
SALES = {"FY23Q1": 2842.2, "FY23Q2": 3223.6, "FY23Q3": 3042.4, "FY23Q4": 3705.9, "FY24Q1": 3018.4, "FY24Q2": 3473.6,
         "FY24Q3": 3057.2, "FY24Q4": 3893.6, "FY25Q1": 3174.68, "FY25Q2": 3646.62, "FY25Q3": 3236.86, "FY25Q4": 4050.79,
         "FY26Q1": 3377.44, "FY26Q2": 3849.89}                 # DICK'S Business net sales $M (digest s.2b / B7)
QSEAS = [3174.68, 3646.62, 3236.86, 4050.79]; QSEAS = [x / sum(QSEAS) for x in QSEAS]
INTRA = {0: [1/3]*3, 1: [1/3]*3, 2: [1/3]*3, 3: [0.28, 0.44, 0.28]}
MSHARE = [QSEAS[(m % 12) // 3] * INTRA[(m % 12) // 3][m % 3] for m in range(12)]
def mi(fy, mon): return FYS.index(fy) * 12 + MN.index(mon)
# (label, fy, month or None, quarter, fmt H/F, n, relocation share, source)  -- from B7 HIST/EVID (10-Q counts + scrape dates)
EV = [
 ("FY23 HoS", "FY23", None, 1, "H", 3, 0.8, "10-Q counts"), ("FY23 HoS", "FY23", None, 2, "H", 4, 0.8, "10-Q"), ("FY23 HoS", "FY23", None, 3, "H", 2, 0.8, "10-Q"),
 *[("FY23 FH", "FY23", None, q, "F", 3, 0.75, "assumed even") for q in (1, 2, 3, 4)],
 ("FY24 HoS", "FY24", None, 1, "H", 2, 6/7, "F2"), ("FY24 HoS", "FY24", None, 3, "H", 3, 6/7, "F2"), ("FY24 HoS", "FY24", None, 4, "H", 2, 6/7, "F2"),
 *[("FY24 FH", "FY24", None, q, "F", n, 11/15, "F2") for q, n in ((1, 3), (2, 4), (3, 4), (4, 4))],
 ("FY25 HoS Q1", "FY25", None, 1, "H", 2, 13/16, "10-K"), ("FY25 HoS Q2", "FY25", None, 2, "H", 1, 13/16, "10-K"),
 ("FY25 Q3 HoS (Aug)", "FY25", "Aug", 3, "H", 3, 13/16, "H05/H07 dates"), ("FY25 Q3 HoS (Sep)", "FY25", "Sep", 3, "H", 5, 13/16, "H05/H07"),
 ("FY25 Q3 HoS (Oct)", "FY25", "Oct", 3, "H", 5, 13/16, "H05/H07"),
 *[(f"FY25 FH Q{q}", "FY25", None, q, "F", n, 13/15, "10-K / 10-Q counts") for q, n in ((1, 4), (2, 4), (3, 6), (4, 1))],
 ("Amherst NY", "FY26", "Mar", 1, "H", 1, 1.0, "H07 (relo assumed)"), ("Cedar Rapids IA", "FY26", "Jun", 2, "H", 1, 1.0, "H03 relo"),
 ("Gaithersburg MD", "FY26", "Jun", 2, "H", 1, 1.0, "H05 in-place"), ("Schaumburg IL", "FY26", "Jun", 2, "H", 1, 1.0, "H03 relo"),
 ("Niles OH", "FY26", "Jun", 2, "H", 1, 1.0, "H02-5 relo"), ("Arlington TX", "FY26", "Jun", 2, "H", 1, 0.0, "H07 net-new"),
 ("FY26 FH Q1", "FY26", None, 1, "F", 2, 0.87, "10-Q count"), ("FY26 FH Q2", "FY26", None, 2, "F", 8, 0.87, "10-Q count"),
]
EVID_FWD = [
 ("Greensburg PA", "FY26", "Aug", 3, "H", 1, 1.0, "H02 opened 8/7 in-place"), ("Annapolis MD", "FY26", "Aug", 3, "H", 1, 1.0, "H02 8/14 in-place"),
 ("Thornton CO", "FY26", "Sep", 3, "H", 1, 0.5, "H02 relo unknown"), ("Raleigh Crabtree", "FY26", "Oct", 3, "H", 1, 0.0, "H02 10/9 infill 6.0mi"),
 ("Frisco Stonebriar", "FY26", "Oct", 3, "H", 1, 1.0, "H02/H03 10/23 next to #421"),
 ("Cherry Hill NJ", "FY26", "Nov", 4, "H", 1, 1.0, "H02 relo confirmed"), ("Novi MI", "FY26", "Nov", 4, "H", 1, 1.0, "H06 hiring; 0.8mi"),
 ("Sioux Falls SD", "FY26", "Dec", 4, "H", 1, 1.0, "H06 hiring; 0.1mi"),
 ("FH 3Q26", "FY26", None, 3, "F", 7, 0.87, "guide ~20 FY26"), ("FH 4Q26", "FY26", None, 4, "F", 3, 0.87, "guide"),
]
CONS_FWD = [("cons HoS 3Q26", "FY26", None, 3, "H", 6, 0.75, "BBG 41->47"), ("cons HoS 4Q26", "FY26", None, 4, "H", 2, 0.75, "BBG 47->49"),
            ("cons FH 3Q26", "FY26", None, 3, "F", 7, 0.87, "BBG 52->59"), ("cons FH 4Q26", "FY26", None, 4, "F", 4, 0.87, "BBG 59->63")]

def engine(events, hos_inc, fh_inc, cannib=0.0):
    inc_m = [0.0] * (NM + 13); can_m = [0.0] * (NM + 13)
    for lab, fy, mon, q, fmt, n, r, src in events:
        months = [(mi(fy, mon), n)] if mon else [(FYS.index(fy) * 12 + (q - 1) * 3 + k, n / 3) for k in range(3)]
        for m0, nn in months:
            for k in range(13):                         # relocated store: in comp at once; increment for 12 months (0.5 / 1 x11 / 0.5)
                mm = m0 + k
                if mm >= NM: break
                w = 0.5 if k in (0, 12) else 1.0
                inc_m[mm] += nn * r * (hos_inc if fmt == "H" else fh_inc) * MSHARE[mm % 12] * w
                if fmt == "H":
                    can_m[mm] += nn * cannib * MSHARE[mm % 12] * w
    res = {}
    for qi, ql in enumerate(QL):
        pyq = f"FY{int(ql[2:4]) - 1}{ql[4:]}"
        if pyq not in SALES: continue
        rng = range(qi * 3, qi * 3 + 3)
        res[ql] = (sum(inc_m[m] for m in rng) / SALES[pyq] * 100, sum(can_m[m] for m in rng) / SALES[pyq] * 100)
    return res

UPLIFT = [("$6M tax-data median", 6.0), ("$12M scrape low", 12.0), ("$16M scrape base", 16.0), ("$20M company/UBS", 20.0),
          ("$22.5M BLS-jobs (21-24)", 22.5)]
FHU = [2.0, 3.0]
TRAIL8 = ["FY24Q3", "FY24Q4", "FY25Q1", "FY25Q2", "FY25Q3", "FY25Q4", "FY26Q1", "FY26Q2"]
lift_rows, legacy_rows = [], []
for path_name, fwd in (("evidence path", EVID_FWD), ("consensus path", CONS_FWD)):
    for ulab, u in UPLIFT:
        for fu in FHU:
            r_h = engine(EV + fwd, u, 0.0); r_f = engine(EV + fwd, 0.0, fu)
            tl = [comp[q] - r_h[q][0] - r_f[q][0] for q in TRAIL8]
            for q in ("FY26Q3", "FY26Q4"):
                hl, fl = r_h[q][0], r_f[q][0]; tot = hl + fl
                implied = CONS[q] - tot
                lift_rows.append([path_name, ulab, fu, q, round(hl, 2), round(fl, 2), round(tot, 2), CONS[q], round(implied, 2),
                                  round(st.mean(tl), 2), round(min(tl), 2), round(st.mean(tl) - implied, 2)])
            legacy_rows.append([path_name, ulab, fu] + [round(v, 2) for v in tl] + [round(st.mean(tl), 2)])
wcsv("q1_format_lift.csv", ["path", "HoS_uplift", "FH_uplift_$M", "quarter", "HoS_lift_pt", "FH_lift_pt", "total_format_lift_pt",
                            "cons_comp", "implied_legacy_comp", "trailing8Q_legacy_avg", "trailing8Q_legacy_min", "decel_vs_trailing_pt"], lift_rows)
wcsv("q1_legacy_trailing.csv", ["path", "HoS_uplift", "FH_uplift"] + TRAIL8 + ["avg"], legacy_rows)
md("T7. Format lift (gross of cannibalisation) and the legacy comp consensus implies - EVIDENCE opening path",
   ["HoS uplift", "FH $M", "Qtr", "HoS pt", "FH pt", "Format pt", "Cons", "Implied legacy", "Trail-8Q legacy avg", "Trail-8Q min", "Decel pt"],
   [r[1:] for r in lift_rows if r[0] == "evidence path"],
   "Evidence path: Q3FY26 HoS 5 (Greensburg 8/7, Annapolis 8/14 relo; Thornton Sep 0.5; Raleigh 10/9 net-new; Frisco 10/23 relo), Q4FY26 HoS 3 relos (Cherry Hill, Novi Nov; Sioux Falls Dec); FH 7/3 at 87% relo. "
   "Consensus path (BBG HoS +6/+2, FH +7/+4) in q1_format_lift.csv. Increment in comp for 12 months from opening (0.5/1x11/0.5 monthly weights), divided by prior-year DICK'S quarterly sales. "
   "Trailing legacy = actual comp minus the same engine's format lift, Q3FY24-Q2FY26 (not adjusted for World Cup in 1H26).")
md("T8. Engine-implied legacy (ex-format) comp, trailing 8 quarters (evidence path)", ["HoS uplift", "FH $M"] + TRAIL8 + ["avg"],
   [r[1:] for r in legacy_rows if r[0] == "evidence path"])
# opening table Q3FY25-Q4FY26
op = []
for qq, hos, hrel, fh, note in (
    ("Q3FY25", 13, "~10.6 relo-eq (FY25: 13 of 16 relos)", 6, "record 13 HoS (Aug 3 / Sep 5 / Oct 5); laps Aug-Oct 2026 = inside Q3FY26, fully out of the 12-month window by Q4FY26"),
    ("Q4FY25", 0, "-", 1, "BBG FH 41->42"),
    ("Q1FY26", 1, "Amherst (relo assumed)", 2, "HoS 35->36; FH 42->44"),
    ("Q2FY26", 5, "4 relo (Cedar Rapids, Gaithersburg, Schaumburg, Niles) + 1 net-new (Arlington)", 8, "HoS 36->41; FH 44->52"),
    ("Q3FY26E", 5, "3.5 relo-eq: Greensburg, Annapolis, Frisco relo; Thornton 0.5; Raleigh net-new infill", 7, "cons HoS +6 (41->47), FH +7"),
    ("Q4FY26E", 3, "3 relo: Cherry Hill, Novi (Nov), Sioux Falls (Dec)", 3, "cons HoS +2 (47->49), FH +4 (59->63)")):
    op.append([qq, hos, hrel, fh, note])
md("T6. HoS / FH openings Q3 FY25 -> Q4 FY26", ["Qtr", "HoS opened", "HoS relocation vs net-new", "FH opened", "Note"], op,
   "Stores inside their first 12 months (i.e. adding increment to comp): Q3FY26 = part-quarter Q3FY25 cohort (Aug cohort ~0.5 month, Sep ~1.5, Oct ~2.5 of the quarter) + Q4FY25-Q3FY26 openings; "
   "Q4FY26 = Q4FY25 FH (Nov-Jan, exiting) + all Q1-Q4 FY26 openings (HoS: Amherst, 5 Q2, 5 Q3, 3 Q4; FH 2+8+7+3).")

# ------------------------------------------------------------------ 5. variance scenarios
SEG = {"FY26Q3": dict(base=3236.86, rev=3436.61, om=7.17, cons=1.69, ly=5.7, ly2=4.3),
       "FY26Q4": dict(base=4050.79, rev=4144.38, om=10.58, cons=1.59, ly=3.1, ly2=6.6)}
# management FY guide (+2.5% / +3.25% / +4.0%) -> implied 2H and Q4 (sales-weighted on FY25 quarterly DICK'S sales)
W = {"FY26Q1": 3174.68, "FY26Q2": 3646.62, "FY26Q3": 3236.86, "FY26Q4": 4050.79}
h1 = 6.0 * W["FY26Q1"] + 4.9 * W["FY26Q2"]
guide = []
for lab, g in (("low 2.5%", 2.5), ("mid 3.25%", 3.25), ("high 4.0%", 4.0)):
    h2 = (g * sum(W.values()) - h1) / (W["FY26Q3"] + W["FY26Q4"])
    q4_if_q3cons = (h2 * (W["FY26Q3"] + W["FY26Q4"]) - 1.69 * W["FY26Q3"]) / W["FY26Q4"]
    guide.append([lab, round(h2, 2), round(h2, 2), round(q4_if_q3cons, 2), round(h2 + 3.1, 2), round(q4_if_q3cons + 3.1, 2)])
cons_fy = (h1 + 1.69 * W["FY26Q3"] + 1.59 * W["FY26Q4"]) / sum(W.values())
md("T9. What management's FY26 DICK'S comp guide (+2.5-4.0%, reaffirmed 2026-08-25) implies for 2H and Q4",
   ["FY guide", "Implied 2H comp", "Q4 if Q3=Q4", "Q4 if Q3 = cons 1.69", "Q4 2-yr (Q3=Q4)", "Q4 2-yr (Q3=cons)"], guide,
   f"Weights = FY25 quarterly DICK'S sales; 1H26 actual 6.0/4.9. Consensus quarters imply FY26 comp {cons_fy:.2f}% (BBG annual row 3.37%). "
   "Stack (2026-08-25): 'Q3 is going to be a bit more difficult than Q4' -> Q4 >= Q3 within the guide.")
tr_leg_16 = [r for r in lift_rows if r[0] == "evidence path" and r[1] == "$16M scrape base" and r[2] == 2.0]
q4_lift16 = [r for r in tr_leg_16 if r[3] == "FY26Q4"][0]; q3_lift16 = [r for r in tr_leg_16 if r[3] == "FY26Q3"][0]
q4_lift6 = [r for r in lift_rows if r[0] == "evidence path" and r[1] == "$6M tax-data median" and r[2] == 2.0 and r[3] == "FY26Q4"][0]
q3_lift6 = [r for r in lift_rows if r[0] == "evidence path" and r[1] == "$6M tax-data median" and r[2] == 2.0 and r[3] == "FY26Q3"][0]
def scen(q):
    s = SEG[q]; lift16 = q4_lift16 if q == "FY26Q4" else q3_lift16; lift6 = q4_lift6 if q == "FY26Q4" else q3_lift6
    g = {x[0]: x for x in guide}
    gq = (lambda lab: g[lab][3]) if q == "FY26Q4" else (lambda lab: 1.69 if False else g[lab][1])
    return [
        ("2-yr held at 7.5% (mgmt FY framing)", round(7.5 - s["ly"], 2)),
        ("2-yr at 6.5%", round(6.5 - s["ly"], 2)),
        ("2-yr at 5.5%", round(5.5 - s["ly"], 2)),
        ("3-yr held at trailing-4Q min (11.5%)", round(11.5 - s["ly"] - s["ly2"], 2)),
        ("3-yr at 10.5%", round(10.5 - s["ly"] - s["ly2"], 2)),
        ("txn -0.5% x ticket +2.5% (decel ~1pt)", round(((1.025) * (0.995) - 1) * 100, 2)),
        ("txn +0.45% (trail-4Q) x ticket +2.0%", round(((1.02) * (1.0045) - 1) * 100, 2)),
        (f"trailing legacy (avg {lift16[9]:.2f}) + format lift ($16M/$2M)", round(lift16[9] + lift16[6], 2)),
        (f"legacy halves to {lift16[9]/2:.2f} + format ($16M/$2M)", round(lift16[9] / 2 + lift16[6], 2)),
        (f"bear: legacy 0.5% + format at $6M/$2M", round(0.5 + lift6[6], 2)),
        ("mgmt guide LOW, Q4 if Q3=cons" if q == "FY26Q4" else "mgmt guide LOW (2H flat split)", g["low 2.5%"][3] if q == "FY26Q4" else g["low 2.5%"][1]),
        ("mgmt guide MID" + (", Q4 if Q3=cons" if q == "FY26Q4" else " (2H flat split)"), g["mid 3.25%"][3] if q == "FY26Q4" else g["mid 3.25%"][1]),
        ("mgmt guide HIGH" + (", Q4 if Q3=cons" if q == "FY26Q4" else " (2H flat split)"), g["high 4.0%"][3] if q == "FY26Q4" else g["high 4.0%"][1]),
    ]
var_rows = []
for q in ("FY26Q4", "FY26Q3"):
    s = SEG[q]
    for lab, c in scen(q):
        dpt = c - s["cons"]; drev = dpt / 100 * s["base"]
        var_rows.append([q, lab, round(c, 2), round(c + s["ly"], 2), round(dpt, 2), round(drev, 1), round(drev / s["rev"] * 1e4),
                         f"{drev * 0.20 * EPS_PER_M:+.3f}", f"{drev * s['om'] / 100 * EPS_PER_M:+.3f}"])
wcsv("q1_variance.csv", ["quarter", "scenario", "comp_%", "2yr", "var_pt", "rev_var_$M", "bps_of_cons_DSG_rev", "EPS_20pct_FT", "EPS_seg_margin_FT"], var_rows)
for q in ("FY26Q4", "FY26Q3"):
    s = SEG[q]
    md(f"T10{'a' if q=='FY26Q4' else 'b'}. {q} comp scenarios vs consensus {s['cons']}% (comp base = FY25 {q[-2:]} DICK'S sales ${s['base']:,.0f}M; cons DSG rev ${s['rev']:,.2f}M; cons seg OM {s['om']}%)",
       ["Scenario", "Comp", "2-yr", "Var pt", "Rev var $M", "bps of cons rev", "EPS @20% FT", f"EPS @{s['om']}% seg OM"],
       [r[1:] for r in var_rows if r[0] == q])

# ------------------------------------------------------------------ console summary
print(f"EPS per $1M pre-tax: {EPS_PER_M:.5f}")
for r in cons_rows: print("cons stack", r)
for r in rank_rows:
    if r[0] == "FY26Q4": print("rank", r)
print(f"2-yr stack q/q change Q3->Q4 cons {cons_d_q3q4} ; Q2A->Q4E {cons_d_q2q4}; hist ex-COVID q/q 2-yr changes <= cons: {n_d1}/{len(d1)}; "
      f"worst: {sorted(d1, key=lambda z: z[1])[:5]}")
print("trailing txn 4Q", tr4_txn, "8Q", tr8_txn, "ticket 4Q", tr4_tkt)
for r in grid: print("grid", r)
print("largest 1q ticket drops", big); print("largest 2q", big2); print("largest y/y", bigy)
for r in lift_rows:
    if r[0] == "evidence path": print("lift", r)
for r in guide: print("guide", r)
print("cons FY26 comp from quarters", round(cons_fy, 2))
for r in var_rows: print("var", r)
MD.insert(0, f"<!-- generated by q1_comp_bridge.py; EPS per $1M pre-tax = {EPS_PER_M:.5f}; 2-yr q/q change cons Q3->Q4 = {cons_d_q3q4}pt "
             f"(hist ex-COVID pairs with drop >= this: {n_d1}/{len(d1)}); Q2A->Q4E = {cons_d_q2q4}pt -->")
open(os.path.join(OUT, "tables.md"), "w", encoding="utf-8").write("\n".join(MD))

