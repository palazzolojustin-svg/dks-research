"""P4: DKS same-store ticket (sales per transaction) / transactions history FY2011 -> Q2 FY2026.
Sources: FY2011-FY2022 DKS 10-Q/10-K MD&A (EDGAR; text saved in raw/P4_edgar/*.txt by P4_edgar_ticket.py);
FY2023-Q2 FY2026 from corpus (W03/W04 10-Q notes, WF Exhibit 18, digest).
Basis: FY2011-FY2016 'at Dick's Sporting Goods stores'; FY2017-FY2022 consolidated same store; FY2023+ DICK'S comp.
Q4 values are DERIVED (INFERENCE) as (FY - 0.68*39wk)/0.32 where 39wk is available; flagged 'derived'.
Rerun: python P4_ticket_history.py -> raw/P4_ticket_history.csv + summary stats printed
"""
import csv, os, statistics as st
RAW = r"C:\Users\palaz\Downloads\DKS_RESEARCH\THESIS_SCRAPE\raw"
# (period, ticket, txn, source_filing_date, note)
Q = [
 ("Q1FY12", 4.0, 3.3, "2012-05-24 10-Q", ""), ("Q2FY12", 4.0, -1.1, "2012-08-23 10-Q", ""), ("Q3FY12", 2.9, 1.0, "2012-11-21 10-Q", ""),
 ("Q1FY13", 2.0, -5.2, "2013-05-31 10-Q", "comp decrease"), ("Q2FY13", 2.0, -1.9, "2013-08-30 10-Q", ""), ("Q3FY13", 1.5, 1.9, "2013-11-27 10-Q", "shifted basis; txn up 'reflects additional advertising, increased store payroll'"),
 ("Q1FY14", 2.5, -0.2, "2014-05-29 10-Q", ""), ("Q2FY14", 1.8, 2.3, "2014-08-28 10-Q", ""), ("Q3FY14", 2.7, -1.0, "2014-11-26 10-Q", ""),
 ("Q1FY15", 1.0, 0.8, "2015-05-28 10-Q", ""), ("Q2FY15", 2.5, -1.0, "2015-08-27 10-Q", ""), ("Q3FY15", 1.2, -0.5, "2015-11-25 10-Q", "record warm weather"),
 ("Q1FY16", 1.0, -0.5, "2016-05-25 10-Q", ""), ("Q2FY16", 1.3, 1.7, "2016-08-25 10-Q", ""), ("Q3FY16", 1.3, 4.2, "2016-11-21 10-Q", "Sports Authority liquidation share gain"),
 ("Q1FY17", 1.6, 0.8, "2017-05-25 10-Q", "consolidated basis from here"), ("Q2FY17", 2.1, -2.0, "2017-08-24 10-Q", ""), ("Q3FY17", 0.0, -0.9, "2017-11-22 10-Q", ""),
 ("Q1FY18", 1.2, -3.7, "2018-05-31 10-Q", "hunt/electronics exit"), ("Q2FY18", 0.7, -4.7, "2018-08-30 10-Q", ""), ("Q3FY18", 1.6, -5.5, "2018-11-29 10-Q", ""),
 ("Q1FY19", 1.0, -1.0, "2019-05-30 10-Q", ""), ("Q2FY19", 2.1, 1.1, "2019-08-29 10-Q", ""), ("Q3FY19", 2.7, 3.3, "2019-11-26 10-Q", ""),
 ("Q1FY20", 9.2, -38.7, "2020-06-03 10-Q", "COVID"), ("Q2FY20", 17.9, 2.8, "2020-08-26 10-Q", "COVID"), ("Q3FY20", 19.6, 3.6, "2020-11-25 10-Q", "COVID"),
 ("Q1FY21", 25.0, 90.0, "2021-05-26 10-Q", "COVID lap"), ("Q2FY21", 7.1, 12.1, "2021-08-25 10-Q", ""), ("Q3FY21", 3.7, 8.5, "2021-11-23 10-Q", ""),
 ("Q1FY22", -2.0, -6.4, "2022-05-25 10-Q", "stimulus lap"), ("Q2FY22", 3.3, -8.4, "2022-08-24 10-Q", ""), ("Q3FY22", 2.8, 3.7, "2022-11-23 10-Q", ""),
 ("Q1FY23", 0.7, 2.7, "W03 / WF Exh18", ""), ("Q2FY23", -1.0, 2.8, "W03 / WF Exh18", ""), ("Q3FY23", 0.6, 1.1, "W03 / WF Exh18", ""), ("Q4FY23", 2.8, 0.0, "WF Exh18", ""),
 ("Q1FY24", 2.6, 2.7, "W03", ""), ("Q2FY24", 3.5, 1.0, "W03", ""), ("Q3FY24", 4.8, -0.6, "W03", ""), ("Q4FY24", 4.4, 2.0, "WF Exh18", ""),
 ("Q1FY25", 3.7, 0.8, "W04", ""), ("Q2FY25", 4.1, 0.9, "W04", ""), ("Q3FY25", 4.4, 1.3, "W04 (WF prints 4.1/1.6)", ""), ("Q4FY25", 4.4, -1.3, "C02B", ""),
 ("Q1FY26", 5.5, 0.5, "W04", ""), ("Q2FY26", 3.6, 1.3, "W04", ""),
]
FY = {  # fiscal year reported ticket, txn ; 39wk (ticket, txn)
 "FY11": (2.4, -1.6, None), "FY12": (3.3, -0.9, (3.6, 0.9)), "FY13": (1.8, 0.6, (1.8, -1.7)), "FY14": (1.9, 1.2, (2.4, 0.4)),
 "FY15": (1.3, -1.2, (1.6, -0.3)), "FY16": (1.6, 2.1, (1.2, 1.8)), "FY17": (0.2, -0.5, (1.2, -0.7)), "FY18": (1.2, -4.3, (1.1, -4.6)),
 "FY19": (2.0, 1.7, (1.9, 1.2)), "FY20": (17.0, -7.1, (15.5, -9.7)), "FY21": (7.7, 18.8, (9.5, 27.1)), "FY22": (0.2, -0.7, (1.1, -3.7)),
 "FY23": (0.8, 1.6, None), "FY24": (4.0, 1.2, (3.7, 1.0)), "FY25": (4.2, 0.3, None),
}
rows = [[p, t, x, s, n, "reported"] for p, t, x, s, n in Q]
for fy, (t, x, w39) in FY.items():
    if w39 and fy not in ("FY23", "FY24"):
        qt = (t - 0.68 * w39[0]) / 0.32; qx = (x - 0.68 * w39[1]) / 0.32
        rows.append(["Q4" + fy, round(qt, 1), round(qx, 1), "derived from FY and 39wk", "INFERENCE +-0.5pt", "derived"])
    rows.append([fy, t, x, "10-K", "", "annual"])
with open(os.path.join(RAW, "P4_ticket_history.csv"), "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["period", "ticket_pct", "transactions_pct", "source", "note", "type"]); w.writerows(rows)

covid = {"Q1FY20", "Q2FY20", "Q3FY20", "Q4FY20", "Q1FY21", "Q2FY21", "Q3FY21", "Q4FY21"}
qt = [r for r in rows if r[5] in ("reported", "derived") and r[0] not in covid]
tick = [r[1] for r in qt]
print("non-COVID quarters:", len(tick), "median ticket %.2f mean %.2f" % (st.median(tick), st.mean(tick)))
print("quarters with ticket <= 1.25:", sum(t <= 1.25 for t in tick), "<= 1.0:", sum(t <= 1.0 for t in tick))
pre = [r[1] for r in qt if any(r[0].endswith(f"FY{y}") for y in range(12, 20))]
print("FY12-FY19 quarters:", len(pre), "mean ticket %.2f median %.2f min %.1f" % (st.mean(pre), st.median(pre), min(pre)))
ann = [FY[k][0] for k in FY if k not in ("FY20", "FY21")]
print("annual ticket ex-COVID FY11-FY25:", ann, "mean %.2f; years positive %d/%d" % (st.mean(ann), sum(a > 0 for a in ann), len(ann)))
low = [(r[0], r[1]) for r in qt if r[1] <= 1.25]
print("low-ticket quarters:", low)
